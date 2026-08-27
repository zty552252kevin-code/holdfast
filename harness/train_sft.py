#!/usr/bin/env python3
"""
HoldFast: SFT a Qwen3 student simulator on rendered dialogues.

Conditioning design (D-011): one model serves all misconceptions — the system
prompt carries the assigned misconception description; dialogue turns alternate
tutor (user) / student (assistant); loss is computed on assistant tokens only.
Qwen3 chat template with enable_thinking=False (D-005).

Runs on the dev machine / training nodes (no internet needed).

Usage (smoke, 0.6B on pilot):
    python train_sft.py --model /data/holdfast/models/Qwen3-0.6B \
        --rendered /data/holdfast/data/pilot/rendered.jsonl \
        --scaffolds /data/holdfast/data/pilot/scaffolds.jsonl \
        --out /data/holdfast/runs/smoke-0.6b --epochs 2
"""

import argparse
import json
import os
import random
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)

STUDENT_SYSTEM = (
    "You are a middle-school student working with a math tutor. You genuinely "
    "hold this specific misconception: {misconception}\n"
    "You consistently apply your (mistaken) method when solving problems and you "
    "are confident in it. You only change your mind if the tutor's explanation "
    "actually addresses your specific mistake; generic prodding or off-target "
    "advice does not sway you. Always answer as the student, in plain text."
)

STUDENT_SYSTEM_CORRECT = (
    "You are a middle-school student working with a math tutor. You understand "
    "this topic correctly and solve problems carefully, showing your steps. "
    "Always answer as the student, in plain text."
)

# zh arm (D-015): student system prompts mirror the EN ones
STUDENT_SYSTEM_ZH = (
    "你是一名正在和数学辅导老师交流的初中学生。你真实地持有下面这个特定的错误认知:{misconception}\n"
    "你解题时始终如一地使用你(错误)的方法,并且对它很有信心。只有当老师的讲解确实针对你这个"
    "具体错误时,你才会改变想法;泛泛的追问或不对症的建议不会动摇你。始终以学生身份、用纯文本回答。"
)

STUDENT_SYSTEM_CORRECT_ZH = (
    "你是一名正在和数学辅导老师交流的初中学生。你正确地理解这个知识点,解题认真,会展示步骤。"
    "始终以学生身份、用纯文本回答。"
)


def build_messages(rec, scaffold):
    zh = scaffold.get("lang") == "zh"
    if (rec["type"] in ("correct", "control_correct")
            or rec.get("malrule_id") in (None, "", "none")):
        system = STUDENT_SYSTEM_CORRECT_ZH if zh else STUDENT_SYSTEM_CORRECT
    else:
        tmpl = STUDENT_SYSTEM_ZH if zh else STUDENT_SYSTEM
        system = tmpl.format(misconception=scaffold["misconception"])
    msgs = [{"role": "system", "content": system}]
    for t in rec["turns"]:
        role = "user" if t["role"] == "tutor" else "assistant"
        if msgs[-1]["role"] == role:  # merge unexpected same-role runs
            msgs[-1]["content"] += "\n" + t["text"]
        else:
            msgs.append({"role": role, "content": t["text"]})
    return msgs


class DialogueDataset(Dataset):
    """Tokenize with the chat template; label-mask everything except assistant
    turn content. Masking is computed by incremental-prefix tokenization, which
    is template-agnostic and exact."""

    def __init__(self, records, scaffolds, tok, max_len):
        self.items = []
        skipped = 0
        for rec in records:
            sc = scaffolds.get(rec["dialogue_id"], {})
            msgs = build_messages(rec, sc)
            ids, labels = self._encode(msgs, tok, max_len)
            if ids is None:
                skipped += 1
                continue
            self.items.append({"input_ids": ids, "labels": labels})
        if skipped:
            print(f"[dataset] skipped {skipped} over-length dialogues")

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

    @staticmethod
    def _encode(msgs, tok, max_len):
        def render(upto, gen_prompt=False):
            return tok.apply_chat_template(
                msgs[:upto], tokenize=True, add_generation_prompt=gen_prompt,
                enable_thinking=False)

        full = render(len(msgs))
        if len(full) > max_len:
            return None, None
        labels = [-100] * len(full)
        for i, m in enumerate(msgs):
            if m["role"] != "assistant":
                continue
            # tokens of this assistant turn = prefix-with-gen-prompt .. prefix-through-turn
            start = len(render(i, gen_prompt=True))
            end = len(render(i + 1))
            for j in range(start, min(end, len(full))):
                labels[j] = full[j]
        return full, labels


def collate(batch, pad_id):
    n = max(len(b["input_ids"]) for b in batch)
    ids, labels, attn = [], [], []
    for b in batch:
        k = n - len(b["input_ids"])
        ids.append(b["input_ids"] + [pad_id] * k)
        labels.append(b["labels"] + [-100] * k)
        attn.append([1] * len(b["input_ids"]) + [0] * k)
    return {"input_ids": torch.tensor(ids), "labels": torch.tensor(labels),
            "attention_mask": torch.tensor(attn)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--scaffolds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--global-batch", type=int, default=16)
    ap.add_argument("--micro-batch", type=int, default=4)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--eval-frac", type=float, default=0.05)
    ap.add_argument("--fsdp", action="store_true",
                    help="full-shard FSDP (8B/14B full-param won't fit DDP)")
    ap.add_argument("--save-epochs", action="store_true",
                    help="mid-run epoch checkpoints incl. optimizer state — "
                         "~96G per checkpoint at 8B, disk bomb; off by default")
    args = ap.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)

    tok = AutoTokenizer.from_pretrained(args.model)
    records = [json.loads(l) for l in open(args.rendered)]
    scaffolds = {json.loads(l)["dialogue_id"]: json.loads(l)
                 for l in open(args.scaffolds)}
    # the scaffold file DEFINES the cell: rendered_main.jsonl holds all scales,
    # a grid cell trains only on its (nested) scaffold subset
    records = [r for r in records if r["dialogue_id"] in scaffolds]
    print(f"[cell] {len(records)} rendered dialogues match "
          f"{len(scaffolds)} scaffolds from {args.scaffolds}")
    random.shuffle(records)
    n_eval = max(4, int(len(records) * args.eval_frac))
    ds_eval = DialogueDataset(records[:n_eval], scaffolds, tok, args.max_len)
    ds_train = DialogueDataset(records[n_eval:], scaffolds, tok, args.max_len)
    print(f"train={len(ds_train)} eval={len(ds_eval)}")

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, attn_implementation="sdpa")
    model.config.use_cache = False

    world = int(os.environ.get("WORLD_SIZE", 1))
    accum = max(1, args.global_batch // (args.micro_batch * world))
    targs = TrainingArguments(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        per_device_train_batch_size=args.micro_batch,
        per_device_eval_batch_size=args.micro_batch,
        gradient_accumulation_steps=accum,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch" if args.save_epochs else "no",
        save_total_limit=1,
        bf16=True,
        seed=args.seed,
        report_to=[],
        remove_unused_columns=False,
        gradient_checkpointing=args.fsdp,
        fsdp="full_shard auto_wrap" if args.fsdp else "",
        fsdp_config={"transformer_layer_cls_to_wrap": ["Qwen3DecoderLayer"]}
        if args.fsdp else None,
    )
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    trainer = Trainer(model=model, args=targs, train_dataset=ds_train,
                      eval_dataset=ds_eval,
                      data_collator=lambda b: collate(b, pad_id))
    trainer.train()
    if args.fsdp:
        # explicit FULL_STATE_DICT gather, cast to bf16 (the gathered master
        # weights are fp32 — halves the final checkpoint), save on rank 0.
        # The gather's offload_to_cpu D2H copies raced ahead of NCCL once and
        # the LAST unit (layer 35 of 8B) landed with stale shard data from
        # ranks>=1 — synchronize around the gather, then verify the written
        # file tensor-by-tensor against an independent materialization.
        from torch.distributed.fsdp import (
            FullyShardedDataParallel as FSDP)

        torch.cuda.synchronize()
        # D-024: NOTHING may touch FSDP state between train() and this gather.
        # The live-gen canary used to run here; at 14B its summon_full_params
        # (materializes the WHOLE model, +28G/GPU) always OOMs partway —
        # deterministically while unsharding layer 25 — and the aborted
        # summon leaves that unit's handle holed (empty views), silently
        # poisoning EVERY subsequent state-dict path (legacy gather, summon,
        # and DCP, which shares the FSDP1 hooks). All three 14B finals lost
        # the same 4 layer-25 tensors this way. The canary now runs AFTER
        # the save. All ranks must enter this call (collective); each rank
        # gets the full sd on CPU.
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

            # integrity gate (D-024): reload every saved tensor from disk and
            # compare against the in-memory gathered sd (write fidelity), plus
            # completeness (numel>0 above, key count below); cold behavioral
            # check is gen_check.py downstream. Replaces the two-path
            # materialization compare, which is unsound on this build.
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

        try:  # live-generation canary AFTER the save (D-024): proves training
            trainer.model.eval()  # didn't corrupt the weights; can no longer
            # poison the gather. Expected to OOM-skip at 14B (summon needs
            # the whole model resident); cold gen_check covers behavior.
            msgs = [{"role": "system", "content": STUDENT_SYSTEM_CORRECT},
                    {"role": "user", "content": "What is 3/4 + 1/4?"}]
            text = tok.apply_chat_template(msgs, tokenize=False,
                                           add_generation_prompt=True,
                                           enable_thinking=False)
            enc = tok(text, return_tensors="pt").to(trainer.args.device)
            with FSDP.summon_full_params(trainer.model, writeback=False), \
                    torch.no_grad():
                out_ids = model.generate(
                    **enc, max_new_tokens=40, do_sample=False,
                    use_cache=False,
                    pad_token_id=tok.pad_token_id or tok.eos_token_id)
            if trainer.is_world_process_zero():
                gen = tok.decode(out_ids[0][enc.input_ids.shape[1]:],
                                 skip_special_tokens=True)
                print("[live-gen]", repr(gen))
        except Exception as e:  # canary only — never kill a finished run
            print("[live-gen] skipped:", e)
    else:
        trainer.save_model(args.out + "/final")
    if trainer.is_world_process_zero():
        tok.save_pretrained(args.out + "/final")
        print("TRAIN DONE ->", args.out + "/final")


if __name__ == "__main__":
    main()
