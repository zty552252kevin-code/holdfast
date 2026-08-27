#!/usr/bin/env python3
"""HoldFast: quick sanity generation after smoke SFT — does the trained
simulator produce the malrule answer on held-out probes? Not a metric run;
probe_eval.py (turn-by-turn, batched) is the real harness."""

import argparse
import json
import random
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, "/data/holdfast/harness")
from train_sft import STUDENT_SYSTEM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/data/holdfast/runs/smoke-0.6b/final")
    ap.add_argument("--probes", default="/data/holdfast/data/probes/probes_hold_en.jsonl")
    ap.add_argument("--scaffolds", default="/data/holdfast/data/pilot/scaffolds.jsonl")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args()

    # misconception descriptions per malrule (from scaffolds; probes carry only ids)
    desc = {}
    for l in open(args.scaffolds):
        sc = json.loads(l)
        if sc.get("malrule_id"):
            desc[sc["malrule_id"]] = sc["misconception"]

    probes = [json.loads(l) for l in open(args.probes)]
    probes = [p for p in probes if p["malrule_id"] in desc]
    rng = random.Random(args.seed)
    sample = rng.sample(probes, min(args.n, len(probes)))

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    n_mal = n_cor = 0
    for p in sample:
        msgs = [
            {"role": "system", "content": STUDENT_SYSTEM.format(
                misconception=desc[p["malrule_id"]])},
            {"role": "user", "content": "Try this one: " + p["problem_text"]},
        ]
        ids = tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True,
                                      enable_thinking=False, return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = model.generate(ids, max_new_tokens=256, do_sample=False,
                                 pad_token_id=tok.eos_token_id)
        text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
        has_mal = p["malrule_answer"] in text
        has_cor = p["correct_answer"] in text and p["correct_answer"] != p["malrule_answer"]
        n_mal += has_mal
        n_cor += has_cor
        print(f"[{p['malrule_id']}] want-wrong={p['malrule_answer']!r} "
              f"correct={p['correct_answer']!r} -> mal={has_mal} cor={has_cor}")
        print("   ", text[:220].replace("\n", " "))
    print(f"\nSANITY: malrule-answer present {n_mal}/{len(sample)}, "
          f"correct-answer present {n_cor}/{len(sample)} (crude substring, not the metric)")


if __name__ == "__main__":
    main()
