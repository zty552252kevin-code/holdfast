#!/usr/bin/env python3
"""
HoldFast: compute one grid row's preregistered tests and print the results-doc
table row (same format as docs/results_interim_20260826.md).

Definitions (PLAN §3, frozen):
- H1 diff = mean_seed(hold_consistency) - base hold, 95% t-CI df=2 (t=4.303)
  over the 3 per-seed diffs; PASS iff CI excludes 0.
- H3 diff = mean_seed(selectivity) - base selectivity, same CI;
  selectivity = targeted_flip - max(misaligned_flip, generic_flip).
- H5 diff = mean_seed(static_correct_acc) - base; BREACH iff < -0.05 (5pp).
- other  = mean_seed(other_frac.dialogue)  (auxiliary).

  usage: row_ci.py SIZE SCALE [--lang en] [--runs /data/holdfast/runs]
         [--cell-prefix en]        # e.g. en-dpo for DPO cells
"""

import argparse
import json
import math
from pathlib import Path

SEEDS = [17, 1017, 2017]
T95_DF2 = 4.303


def ci_diff(vals, base):
    diffs = [v - base for v in vals]
    n = len(diffs)
    m = sum(diffs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in diffs) / (n - 1))
    h = T95_DF2 * sd / math.sqrt(n)
    return m, m - h, m + h


def sel(p):
    return (p["targeted_flip"]["rate"]
            - max(p["misaligned_flip"]["rate"], p["generic_flip"]["rate"]))


def r3(x):
    return ("%.3f" % x).replace("0.", ".", 1) if x >= 0 else (
        "%.3f" % x).replace("-0.", "-.", 1)


def sgn(x):
    return "%+.3f" % x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("size")
    ap.add_argument("scale")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--cell-prefix", default="",
                    help="override cell prefix (default = lang; use en-dpo "
                         "for the DPO arm)")
    ap.add_argument("--runs", default="/data/holdfast/runs")
    args = ap.parse_args()
    runs = Path(args.runs)
    prefix = args.cell_prefix or args.lang

    cells = []
    for seed in SEEDS:
        p = runs / ("grid/%s-%s-%s-s%d/eval/preview.json"
                    % (prefix, args.size, args.scale, seed))
        cells.append(json.load(open(p)))
    base = json.load(open(
        runs / ("baselines/%s-%s-base/preview.json" % (args.lang, args.size))))

    holds = [c["hold_consistency"]["rate"] for c in cells]
    h1m, h1lo, h1hi = ci_diff(holds, base["hold_consistency"]["rate"])
    h1 = "PASS" if (h1lo > 0 or h1hi < 0) else "FAIL"
    sels = [sel(c) for c in cells]
    h3m, h3lo, h3hi = ci_diff(sels, sel(base))
    h3 = "PASS" if (h3lo > 0 or h3hi < 0) else "FAIL"
    accs = [c["static_correct_acc"]["rate"] for c in cells]
    h5m = sum(accs) / len(accs) - base["static_correct_acc"]["rate"]
    h5 = "OK" if h5m >= -0.05 else "BREACH"
    other = sum(c["other_frac"]["dialogue"] for c in cells) / len(cells)

    h5s = ("**%s**" % ("−" + sgn(h5m)[1:]) if h5 == "BREACH"
           else sgn(h5m).replace("-", "−"))
    h5f = "**BREACH**" if h5 == "BREACH" else "OK"
    print("| %s | %s | %s | %s | %s [%s,%s] | %s | %s [%s,%s] | %s | %s | %s"
          " | %.2f |" % (
              args.size, args.scale,
              "/".join(r3(h) for h in holds),
              r3(base["hold_consistency"]["rate"]),
              sgn(h1m), sgn(h1lo), sgn(h1hi), h1,
              sgn(h3m), sgn(h3lo), sgn(h3hi), h3,
              h5s, h5f, other))
    print("(base selectivity %s: %+.3f; trained sel %s)"
          % (args.size, sel(base), "/".join("%.3f" % s for s in sels)))


if __name__ == "__main__":
    main()
