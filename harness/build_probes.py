#!/usr/bin/env python3
"""
HoldFast: build & freeze held-out probe sets (PLAN §3, §5).

Two files per language:
  probes_hold_{lang}.jsonl     — per-malrule probes where malrule != correct answer
                                 (turn-probe consistency + flip metrics)
  probes_correct_{lang}.jsonl  — correct-solving probes (H5 collateral damage)

Frozen with SHA-256 recorded in docs/DECISIONS.md at preregistration freeze.
Top-level seed (20269999) is disjoint from training-data seeds by convention;
on top of that, training-side generation must exclude any problem_text that
appears in these files (use --exclude-probes in the scale-up generator).

Usage:
    python build_probes.py --per-malrule 20 --per-malrule-correct 10
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

MALRULELIB = Path.home() / "malrulelib"
sys.path.insert(0, str(MALRULELIB))

import datagen  # noqa: E402

from gen_scaffolds import EXCLUDED, load_pool, sample_problem  # noqa: E402

ROOT = Path(__file__).parent.parent


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(pool, rng, per_malrule, require_differ):
    rows = []
    for module_path, gen_cls, mal, cor, caps in pool:
        seen_texts = set()
        got, tries = 0, 0
        while got < per_malrule and tries < per_malrule * 8:
            tries += 1
            p = sample_problem(gen_cls, mal, cor, caps, rng,
                               require_differ=require_differ)
            if p is None or p["problem_text"] in seen_texts:
                continue
            seen_texts.add(p["problem_text"])
            rows.append({
                "probe_id": f"{module_path}::{got:03d}",
                "malrule_id": module_path,
                "malrule_name": mal.get_name(),
                "seed": p["seed"], "level": p["level"], "difficulty": p["difficulty"],
                "problem_text": p["problem_text"],
                "correct_answer": p["correct_answer"],
                "malrule_answer": p["malrule_answer"],
            })
            got += 1
        if got < per_malrule:
            print(f"  [warn] {module_path}: only {got}/{per_malrule} unique probes")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20269999)
    ap.add_argument("--per-malrule", type=int, default=20)
    ap.add_argument("--per-malrule-correct", type=int, default=10)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--outdir", default=str(ROOT / "data/probes"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    pool, skipped = load_pool()
    print(f"usable malrules: {len(pool)}  skipped: {len(skipped)}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    hold = build(pool, rng, args.per_malrule, require_differ=True)
    correct = build(pool, rng, args.per_malrule_correct, require_differ=False)

    for name, rows in [(f"probes_hold_{args.lang}.jsonl", hold),
                       (f"probes_correct_{args.lang}.jsonl", correct)]:
        path = outdir / name
        with path.open("w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{name}: {len(rows)} probes  sha256={sha256_file(path)}")


if __name__ == "__main__":
    main()
