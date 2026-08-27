#!/usr/bin/env python3
"""
HoldFast DPO readout (Amendment A-1): paired-by-seed diffs of the DPO cell
minus the same-size same-seed 4k SFT cell, 95% t-CI (df=2, t=4.303) over the
3 paired diffs. Either direction is reportable (A-1: "either direction").

Metrics: hold_consistency, targeted_flip, misaligned_flip, generic_flip,
selectivity (targeted - max(misaligned, generic)), static_correct_acc.

  usage: dpo_ci.py SIZE [--runs /data/holdfast/runs]
"""

import argparse
import json
import math
from pathlib import Path

SEEDS = [17, 1017, 2017]
T95_DF2 = 4.303


def sel(p):
    return (p["targeted_flip"]["rate"]
            - max(p["misaligned_flip"]["rate"], p["generic_flip"]["rate"]))


METRICS = [
    ("hold", lambda p: p["hold_consistency"]["rate"]),
    ("targeted", lambda p: p["targeted_flip"]["rate"]),
    ("misaligned", lambda p: p["misaligned_flip"]["rate"]),
    ("generic", lambda p: p["generic_flip"]["rate"]),
    ("selectivity", sel),
    ("H5 acc", lambda p: p["static_correct_acc"]["rate"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("size")
    ap.add_argument("--runs", default="/data/holdfast/runs")
    args = ap.parse_args()
    runs = Path(args.runs)

    dpo, sft = [], []
    for seed in SEEDS:
        dpo.append(json.load(open(
            runs / ("grid/en-dpo-%s-4k-s%d/eval/preview.json"
                    % (args.size, seed)))))
        sft.append(json.load(open(
            runs / ("grid/en-%s-4k-s%d/eval/preview.json"
                    % (args.size, seed)))))

    print("DPO vs SFT, %s-4k, paired by seed (A-1)" % args.size)
    print("| metric | SFT (3 seeds) | DPO (3 seeds) | paired diff [95% CI] |")
    print("|---|---|---|---|")
    for name, f in METRICS:
        ds = [f(d) - f(s) for d, s in zip(dpo, sft)]
        m = sum(ds) / 3
        sd = math.sqrt(sum((x - m) ** 2 for x in ds) / 2)
        h = T95_DF2 * sd / math.sqrt(3)
        star = " *" if (m - h > 0 or m + h < 0) else ""
        print("| %s | %s | %s | %+.3f [%+.3f,%+.3f]%s |" % (
            name,
            "/".join("%.3f" % f(s) for s in sft),
            "/".join("%.3f" % f(d) for d in dpo),
            m, m - h, m + h, star))
    print("(* = CI excludes 0)")


if __name__ == "__main__":
    main()
