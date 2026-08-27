#!/usr/bin/env python3
"""D-025 drift gate for DPO cells: a lr-5e-7 one-epoch DPO final must sit
within a whisker of its SFT init (healthy: max-abs-diff ~1e-3; the D-016
stale-shard race leaves tensors at 2.6-17.6). Any tensor over --max-diff,
or any missing/shape-mismatched/empty tensor, fails the gate and renames
final -> final.CORRUPT-diff. CPU-only; safe to run while GPUs are busy.

usage: ckpt_diff_gate.py FINAL_DIR INIT_DIR [--max-diff 0.5]
"""
import argparse
import glob
import os
import sys

import torch
from safetensors import safe_open


def index(d):
    m = {}
    for f in sorted(glob.glob(os.path.join(d, "*.safetensors"))):
        with safe_open(f, framework="pt") as sf:
            for k in sf.keys():
                m[k] = f
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("final")
    ap.add_argument("init")
    ap.add_argument("--max-diff", type=float, default=0.5)
    args = ap.parse_args()

    a, b = index(args.init), index(args.final)
    bad = []
    if set(a) != set(b):
        bad.append("key sets differ: %d init vs %d final"
                    % (len(a), len(b)))
    worst = (0.0, "")
    for k in sorted(set(a) & set(b)):
        with safe_open(a[k], framework="pt") as sa, \
                safe_open(b[k], framework="pt") as sb:
            ta, tb = sa.get_tensor(k), sb.get_tensor(k)
        if tb.numel() == 0 or ta.shape != tb.shape:
            bad.append("%s: shape %s vs %s" % (k, ta.shape, tb.shape))
            continue
        mx = (ta.float() - tb.float()).abs().max().item()
        if mx > worst[0]:
            worst = (mx, k)
        if mx > args.max_diff:
            bad.append("%s: max-abs-diff %.4f" % (k, mx))
    print("[diff-gate] worst drift %.5f (%s), threshold %.2f"
          % (worst[0], worst[1], args.max_diff))
    if bad:
        corrupt = args.final.rstrip("/") + ".CORRUPT-diff"
        os.rename(args.final, corrupt)
        print("[diff-gate] FAILED (%d problems, sample: %s) — renamed to %s"
              % (len(bad), bad[:5], corrupt), file=sys.stderr)
        sys.exit(1)
    print("[diff-gate] PASS: all %d tensors within %.2f of init"
          % (len(b), args.max_diff))


if __name__ == "__main__":
    main()
