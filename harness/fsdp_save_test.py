#!/usr/bin/env python3
"""
FSDP save-path bug isolation (devbox NGC torch 2.5.0a0): the Trainer/accelerate
FULL_STATE_DICT gather corrupts the LAST wrapped layer's MLP (layer 35 of 8B,
maxdiff 28 vs base after 6 tiny steps). Train 0.6B for 1 step at lr=0 (saved
weights MUST equal base), then save via three paths and diff each against base:
  A. trainer.save_model (accelerate full-gather — the suspect)
  B. explicit torch FSDP FULL_STATE_DICT gather + save_pretrained
  C. DCP sharded save + accelerate merge_fsdp_weights
Run: torchrun --nproc_per_node=4 harness/fsdp_save_test.py
"""

import json
import sys
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)

sys.path.insert(0, str(Path(__file__).parent))

BASE = "/data/holdfast/models/Qwen3-0.6B"
OUT = "/data/holdfast/runs/fsdp-save-test"


class TinyDS(Dataset):
    def __init__(self, tok):
        ids = tok("The tutor asked a question and the student answered it "
                  "carefully with steps.").input_ids
        self.item = {"input_ids": ids, "labels": ids}

    def __len__(self):
        return 8

    def __getitem__(self, i):
        return self.item


def collate(batch):
    ids = torch.tensor([b["input_ids"] for b in batch])
    return {"input_ids": ids, "labels": ids.clone(),
            "attention_mask": torch.ones_like(ids)}


def diff_vs_base(save_dir, tag):
    from safetensors import safe_open
    base_idx = Path(BASE) / "model.safetensors.index.json"
    if base_idx.exists():
        bm = json.load(open(base_idx))["weight_map"]
    else:
        bm = None  # single-file base
    d = Path(save_dir)
    fidx = d / "model.safetensors.index.json"
    if fidx.exists():
        fm = json.load(open(fidx))["weight_map"]
    else:
        single = d / "model.safetensors"
        if not single.exists():
            print(f"[{tag}] NO OUTPUT FILE")
            return
        with safe_open(single, framework="pt") as f:
            fm = {k: "model.safetensors" for k in f.keys()}
    cache = {}

    def get(root, wm, k):
        if wm is None:
            f = str(Path(root) / "model.safetensors")
        else:
            f = str(Path(root) / wm[k])
        if f not in cache:
            cache[f] = safe_open(f, framework="pt")
        return cache[f].get_tensor(k)

    if bm is None:
        with safe_open(Path(BASE) / "model.safetensors", framework="pt") as f:
            bkeys = set(f.keys())
    else:
        bkeys = set(bm)
    fkeys = set(fm)
    missing = bkeys - fkeys
    bad, worst = 0, ("", 0.0)
    for k in sorted(fkeys & bkeys):
        a = get(save_dir, fm, k).float()
        b = get(BASE, bm, k).float()
        if a.shape != b.shape:
            print(f"[{tag}] SHAPE {k} {tuple(a.shape)} vs {tuple(b.shape)}")
            bad += 1
            continue
        md = (a - b).abs().max().item()
        if md > 1e-3:
            bad += 1
            if md > worst[1]:
                worst = (k, md)
    print(f"[{tag}] keys={len(fkeys)} missing_vs_base={len(missing)} "
          f"bad={bad} worst={worst}")


def main():
    global BASE
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--grad-ckpt", action="store_true")
    ap.add_argument("--epoch-saves", action="store_true",
                    help="save+eval each epoch (2 epochs) before final save, "
                         "reproducing the 8B smoke's multiple mid-run gathers")
    ap.add_argument("--model", default=BASE)
    a = ap.parse_args()
    BASE = a.model

    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, attn_implementation="sdpa")
    model.config.use_cache = False
    extra = {}
    if a.epoch_saves:
        extra = dict(num_train_epochs=2, save_strategy="epoch",
                     eval_strategy="epoch", save_total_limit=1)
    else:
        extra = dict(max_steps=1, save_strategy="no")
    targs = TrainingArguments(
        output_dir=OUT, learning_rate=0.0,
        per_device_train_batch_size=2, bf16=True, report_to=[],
        remove_unused_columns=False, logging_steps=1,
        gradient_checkpointing=a.grad_ckpt,
        fsdp="full_shard auto_wrap",
        fsdp_config={"transformer_layer_cls_to_wrap": ["Qwen3DecoderLayer"]},
        **extra,
    )
    ds = TinyDS(tok)
    trainer = Trainer(model=model, args=targs, train_dataset=ds,
                      eval_dataset=ds if a.epoch_saves else None,
                      data_collator=collate)
    trainer.train()

    # A. suspect path: Trainer/accelerate full gather
    trainer.save_model(OUT + "/final_full")

    # B. explicit torch gather
    from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
    from torch.distributed.fsdp import FullStateDictConfig, StateDictType
    cfg = FullStateDictConfig(offload_to_cpu=True, rank0_only=True)
    with FSDP.state_dict_type(trainer.model, StateDictType.FULL_STATE_DICT,
                              cfg):
        sd = trainer.model.state_dict()
    if trainer.is_world_process_zero():
        sd = {k.replace("_fsdp_wrapped_module.", ""): v.to(torch.bfloat16)
              for k, v in sd.items()}
        model.save_pretrained(OUT + "/final_torch", state_dict=sd,
                              safe_serialization=True)

    trainer.accelerator.wait_for_everyone()
    if trainer.is_world_process_zero():
        for tag, d in [("A trainer.save_model", OUT + "/final_full"),
                       ("B torch gather", OUT + "/final_torch")]:
            diff_vs_base(d, tag)
        print("TEST DONE")


if __name__ == "__main__":
    main()
