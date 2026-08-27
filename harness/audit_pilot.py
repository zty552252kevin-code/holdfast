#!/usr/bin/env python3
"""
HoldFast: audit rendered pilot dialogues.

Automated pass: re-runs the same hard checks as render_dialogues.py (belt and
suspenders) plus heuristic leak scans, and prints summary stats.
Hand-audit pass: writes a readable markdown sample for human review — the
preregistered bar is tutor answer-leak <2% (PLAN §5).

Usage:
    python audit_pilot.py --rendered ../data/pilot/rendered.jsonl --sample 30
"""

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent


def contains_token(text, ans):
    a = str(ans).strip()
    if not a:
        return True
    pat = re.escape(a).replace("\\ ", "\\s*")
    return re.search(rf"(?<![\w/.]){pat}(?![\w/])(?!\.\d)(?!,\d)", text) is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rendered", default=str(ROOT / "data/pilot/rendered.jsonl"))
    ap.add_argument("--scaffolds", default=str(ROOT / "data/pilot/scaffolds.jsonl"))
    ap.add_argument("--sample", type=int, default=30)
    ap.add_argument("--out-md", default=str(ROOT / "data/pilot/hand_audit_sample.md"))
    args = ap.parse_args()

    scaffolds = {json.loads(l)["dialogue_id"]: json.loads(l) for l in open(args.scaffolds)}
    rendered = [json.loads(l) for l in open(args.rendered)]
    print(f"rendered dialogues: {len(rendered)}")
    print(f"by type: {dict(Counter(r['type'] for r in rendered))}")
    print(f"attempts histogram: {dict(Counter(r.get('attempts', 1) for r in rendered))}")

    # Heuristic leak scan: correct answer appearing in ANY pre-remediation tutor turn
    leaks, correct_rule_hints = [], []
    for r in rendered:
        sc = scaffolds[r["dialogue_id"]]
        remediation_seen = False
        for t in r["turns"]:
            if t["kind"].startswith("remediate"):
                remediation_seen = True
                if t["kind"] == "remediate_targeted":
                    continue
            p = sc["problems"][t["slot"]]
            ca, ma = p["correct_answer"], p["malrule_answer"]
            if t["role"] == "tutor" and not remediation_seen and ca != ma \
               and not contains_token(p["problem_text"], ca) \
               and contains_token(t["text"], ca):
                leaks.append((r["dialogue_id"], t["kind"]))
            # crude method-hint scan: tutor names correct first step verb before remediation
            if t["role"] == "tutor" and not remediation_seen and t["kind"] != "present":
                first_ops = " ".join(p["correct_steps"][:4]).lower()
                for verb in ("common denominator", "inverse operation", "distribute",
                             "reciprocal", "borrow", "carry the"):
                    if verb in t["text"].lower() and verb in first_ops:
                        correct_rule_hints.append((r["dialogue_id"], t["kind"], verb))

    n = len(rendered)
    print(f"\nAUTO LEAK SCAN: {len(leaks)}/{n} dialogues with pre-remediation tutor "
          f"answer-leak = {100 * len(leaks) / max(n, 1):.1f}%  (prereg bar <2%)")
    for d, k in leaks[:10]:
        print(f"  leak: {d} at {k}")
    print(f"method-hint flags (review by hand, may be fine): {len(correct_rule_hints)}")
    for d, k, verb in correct_rule_hints[:10]:
        print(f"  hint: {d} at {k}: '{verb}'")

    # Hand-audit sample markdown
    rng = random.Random(7)
    sample = rng.sample(rendered, min(args.sample, len(rendered)))
    lines = ["# HoldFast pilot — hand-audit sample", "",
             "Check per dialogue: (a) tutor leaks answer/method before remediation? "
             "(b) student surface text contradicts computed math? "
             "(c) misaligned remediation accidentally on-target? "
             "(d) natural enough to train on?", ""]
    for r in sample:
        sc = scaffolds[r["dialogue_id"]]
        lines.append(f"## {r['dialogue_id']}  ({r['malrule_id']})")
        lines.append(f"*misconception*: {sc['misconception'][:200]}")
        for i, p in enumerate(sc["problems"]):
            lines.append(f"*slot {i}*: {p['problem_text']}  wrong={p['malrule_answer']}  "
                         f"correct={p['correct_answer']}")
        lines.append("")
        for t in r["turns"]:
            lines.append(f"**{t['role'].upper()}** ({t['kind']}): {t['text']}")
            lines.append("")
        lines.append("- [ ] leak  - [ ] math-contradiction  - [ ] misaligned-on-target  - [ ] unnatural")
        lines.append("")
    Path(args.out_md).write_text("\n".join(lines))
    print(f"\nhand-audit sample ({len(sample)} dialogues) -> {args.out_md}")


if __name__ == "__main__":
    main()
