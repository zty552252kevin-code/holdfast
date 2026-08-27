#!/usr/bin/env python3
"""
HoldFast DPO arm (Amendment A-1): thin TRL wrapper on top of the SFT recipe.

- init policy AND reference from the same-size same-seed 4k SFT cell ckpt
- pairs from make_dpo_pairs.py (balanced file); prompt rendered with the SAME
  chat template discipline as SFT (enable_thinking=False)
- recipe frozen in A-1: beta 0.1, lr 5e-7, 1 epoch, global batch 32, cosine +
  3% warmup (mirrors D-014); overlong pairs dropped, not truncated (count
  reported) — silent truncation could cut the math out of a prompt
- 8B needs --fsdp (+ --precompute-ref frees the ref copy before optimizer
  states allocate); checkpoint saved via the same FULL_STATE_DICT gather as
  train_sft, gen_check.py validates post-hoc (D-016)

Usage (per cell):
  torchrun --nproc_per_node=4 train_dpo.py --model runs/grid/en-8B-4k-s17/final \
      --pairs data/dpo/pairs_en_4k.jsonl --out runs/grid/en-dpo-8B-4k-s17 \
      --seed 17 --fsdp --precompute-ref
"""

import argparse
import json
import os
import random

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer


def build_rows(pairs, tok, max_len, max_prompt_len):
    rows, dropped = [], 0
    for p in pairs:
        prompt = tok.apply_chat_template(
            p["messages"], tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
        n_prompt = len(tok(prompt, add_special_tokens=False)["input_ids"])
        n_worst = n_prompt + 1 + max(
            len(tok(p["chosen"], add_special_tokens=False)["input_ids"]),
            len(tok(p["rejected"], add_special_tokens=False)["input_ids"]))
        if n_prompt > max_prompt_len or n_worst > max_len:
            dropped += 1
            continue
        rows.append({"prompt": prompt, "chosen": p["chosen"],
                     "rejected": p["rejected"]})
    print("[pairs] kept=%d dropped-overlong=%d" % (len(rows), dropped))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="SFT cell final ckpt")
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=float, default=1)
    ap.add_argument("--lr", type=float, default=5e-7)
    ap.add_argument("--beta", type=float, default=0.1)
    ap.add_argument("--global-batch", type=int, default=32)
    ap.add_argument("--micro-batch", type=int, default=1)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--max-prompt-len", type=int, default=1536)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--fsdp", action="store_true")
    ap.add_argument("--precompute-ref", action="store_true",
                    help="precompute ref logps then free the ref copy")
    args = ap.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)

    tok = AutoTokenizer.from_pretrained(args.model)
    pairs = [json.loads(l) for l in open(args.pairs)]
    rows = build_rows(pairs, tok, args.max_len, args.max_prompt_len)
    random.shuffle(rows)
    ds = Dataset.from_list(rows)

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, attn_implementation="sdpa")
    model.config.use_cache = False

    if args.fsdp and args.precompute_ref:
        # TRL precomputes ref logps inside get_train_dataloader(), which runs
        # BEFORE accelerate places/shards the model under FSDP (placement is
        # deferred for FSDP, unlike DDP where Trainer.__init__ moves it) —
        # the ref forward then sees CPU weights vs CUDA batches and dies.
        # Pre-placing the bf16 model on this rank's GPU makes the precompute
        # forward valid; FSDP afterwards shards from GPU params as usual.
        model.to("cuda:%d" % int(os.environ.get("LOCAL_RANK", 0)))

    world = int(os.environ.get("WORLD_SIZE", 1))
    accum = max(1, args.global_batch // (args.micro_batch * world))
    targs = DPOConfig(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        beta=args.beta,
        max_length=args.max_len,
        max_prompt_length=args.max_prompt_len,
        precompute_ref_log_probs=args.precompute_ref,
        per_device_train_batch_size=args.micro_batch,
        gradient_accumulation_steps=accum,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        eval_strategy="no",
        save_strategy="no",
        bf16=True,
        seed=args.seed,
        report_to=[],
        remove_unused_columns=False,
        gradient_checkpointing=args.fsdp,
        fsdp="full_shard auto_wrap" if args.fsdp else "",
        fsdp_config={"transformer_layer_cls_to_wrap": ["Qwen3DecoderLayer"]}
        if args.fsdp else None,
    )
    trainer = DPOTrainer(model=model, ref_model=None, args=targs,
                         train_dataset=ds, processing_class=tok)
    trainer.train()

    if args.fsdp:
        # D-025: this used to be a bare legacy FULL_STATE_DICT gather with no
        # synchronize and no verify — the D-016 D2H-vs-NCCL race hit it in
        # ALL THREE 8B cells (stale shard data in layer 35, the last unit;
        # forensic: 5 tensors with max-abs-diff 2.6–17.6 vs the SFT init
        # while the other 394 sit at ~3e-5). Same treatment as train_sft
        # D-024: synchronize + DCP gather + empty-tensor refusal + disk
        # write-fidelity verify. All ranks must enter the gather (collective).
        torch.cuda.synchronize()
        from torch.distributed.checkpoint.state_dict import (
            StateDictOptions, get_model_state_dict)
        sd = get_model_state_dict(
            trainer.model,
            options=StateDictOptions(full_state_dict=True, cpu_offload=True))
        torch.cuda.synchronize()
        if trainer.is_world_process_zero():
            sd = {k.replace("_fsdp_wrapped_module.", ""):
                  v.to(torch.bfloat16) for k, v in sd.items()}
            empty = [k for k, v in sd.items() if v.numel() == 0]
            if empty:
                raise RuntimeError(
                    f"gather produced {len(empty)} empty tensors "
                    f"(sample: {empty[:6]}) — refusing to save")
            model.save_pretrained(args.out + "/final", state_dict=sd,
                                  safe_serialization=True)
            import glob
            from safetensors import safe_open
            bad, seen = [], 0
            for f in sorted(glob.glob(args.out + "/final/*.safetensors")):
                with safe_open(f, framework="pt") as sf:
                    for k in sf.keys():
                        seen += 1
                        t = sf.get_tensor(k)
                        lk = sd.get(k)
                        if lk is not None and lk.device.type != "cpu":
                            lk = lk.cpu()
                        if (lk is None or t.numel() == 0
                                or lk.shape != t.shape
                                or not torch.equal(lk, t)):
                            bad.append(k)
            if seen != len(sd):
                bad.append(f"tensor count {seen} != gathered {len(sd)}")
            if bad:
                os.rename(args.out + "/final", args.out + "/final.CORRUPT")
                raise RuntimeError(
                    f"checkpoint verify FAILED ({len(bad)} problems, "
                    f"sample: {bad[:8]}) — final/ renamed to final.CORRUPT")
            print(f"[verify] all {seen} saved tensors nonempty and match "
                  f"the gathered state dict")
        del sd
    elif trainer.is_world_process_zero():
        trainer.model.save_pretrained(args.out + "/final",
                                      safe_serialization=True)
    if trainer.is_world_process_zero():
        tok.save_pretrained(args.out + "/final")
        print("DPO DONE ->", args.out + "/final")


if __name__ == "__main__":
    main()
