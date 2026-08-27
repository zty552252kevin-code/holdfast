#!/usr/bin/env python3
"""
Post-train generation spot-check (D-016): a corrupted save reads as a
trained-model failure downstream — refuse to hand a degenerate checkpoint to
eval. Greedy 60 tokens on two correct-persona prompts; degeneracy heuristics:
near-empty output, <25% distinct tokens, or one 4-gram repeated >=5 times.

  usage: gen_check.py CKPT_DIR      (exit 0 = pass, 1 = degenerate)
"""

import sys
from collections import Counter

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PERSONA = ("You are a middle-school student working with a math tutor. You "
           "understand this topic correctly and solve problems carefully, "
           "showing your steps.")
PROMPTS = ["What is 3/4 + 1/4? Show your steps.",
           "Solve 2x + 6 = 14. Show your steps."]


def degenerate(toks):
    if len(toks) < 8:
        return "too-short"
    if len(set(toks)) / len(toks) < 0.25:
        return "low-diversity"
    grams = Counter(tuple(toks[i:i + 4]) for i in range(len(toks) - 3))
    g, c = grams.most_common(1)[0]
    if c >= 5:
        return f"4gram-loop x{c}"
    return None


def main():
    ckpt = sys.argv[1]
    tok = AutoTokenizer.from_pretrained(ckpt)
    model = AutoModelForCausalLM.from_pretrained(
        ckpt, torch_dtype=torch.bfloat16, device_map="cuda")
    fails = 0
    for p in PROMPTS:
        msgs = [{"role": "system", "content": PERSONA},
                {"role": "user", "content": p}]
        text = tok.apply_chat_template(msgs, tokenize=False,
                                       add_generation_prompt=True,
                                       enable_thinking=False)
        enc = tok(text, return_tensors="pt").to(model.device)
        out = model.generate(**enc, max_new_tokens=60, do_sample=False,
                             pad_token_id=tok.pad_token_id or
                             tok.eos_token_id)
        new = out[0][enc.input_ids.shape[1]:].tolist()
        verdict = degenerate(new)
        txt = tok.decode(new, skip_special_tokens=True)[:120]
        print(f"[gen-check] {'FAIL ' + verdict if verdict else 'ok'} :: "
              f"{txt!r}")
        fails += bool(verdict)
    if fails:
        sys.exit(1)
    print("GEN CHECK PASS")


if __name__ == "__main__":
    main()
