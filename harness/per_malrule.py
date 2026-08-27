#!/usr/bin/env python3
"""
HoldFast Appendix D: per-malrule breakdown for one grid row (3 seeds pooled).

Same probe-record definitions as aggregate.py (the frozen prereg metrics),
just grouped by malrule_id:
- hold: P(malrule | type=hold, k>=1)
- targeted / misaligned flip: P(correct | type=flip_*, k>=3)
- other_hold: P(other | type=hold, k>=1)  (measurement-artifact tracer;
  the 'other' audit showed truncation artifacts concentrate in expression/
  ratio/united answer forms, so per-malrule other rates locate them)

Pooling across seeds is descriptive (appendix), not a prereg test — per-
malrule n is too small for per-seed CIs.

  usage: per_malrule.py [--size 8B] [--scale 4k] [--runs /data/holdfast/runs]
                        [--lang en] [--out out.md]
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

SEEDS = [17, 1017, 2017]


def load_row(runs, lang, size, scale):
    recs = []
    for seed in SEEDS:
        d = runs / ("grid/%s-%s-%s-s%d/eval" % (lang, size, scale, seed))
        files = sorted(d.glob("dialogue.shard*.jsonl"))
        if not files:
            print("WARN: no shards under %s" % d)
        for f in files:
            for line in open(f):
                r = json.loads(line)
                if r.get("mode") == "dialogue" and "classification" in r:
                    recs.append(r)
    return recs


def rate(recs, want):
    return (sum(1 for r in recs if r["classification"] == want) / len(recs)
            if recs else None)


def fmt(v):
    return "-" if v is None else "%.2f" % v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="8B")
    ap.add_argument("--scale", default="4k")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--runs", default="/data/holdfast/runs")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    recs = load_row(Path(args.runs), args.lang, args.size, args.scale)
    by_mr = defaultdict(list)
    for r in recs:
        by_mr[r["malrule_id"]].append(r)

    rows = []
    for mr, group in by_mr.items():
        hold = [r for r in group if r["type"] == "hold" and r["k"] >= 1]
        tf = [r for r in group if r["type"] == "flip_targeted" and r["k"] >= 3]
        mf = [r for r in group
              if r["type"] == "flip_misaligned" and r["k"] >= 3]
        rows.append({
            "malrule": mr,
            "hold": rate(hold, "malrule"), "n_hold": len(hold),
            "other_hold": rate(hold, "other"),
            "targeted": rate(tf, "correct"), "n_tf": len(tf),
            "misaligned": rate(mf, "correct"), "n_mf": len(mf),
        })
    rows.sort(key=lambda r: (r["hold"] is None, r["hold"]))

    holds = [r["hold"] for r in rows if r["hold"] is not None]
    lines = []
    lines.append("## Appendix D: per-malrule breakdown — %s-%s-%s "
                 "(3 seeds pooled, descriptive)" %
                 (args.lang, args.size, args.scale))
    lines.append("")
    lines.append("%d malrules with dialogue probes; hold rate: min %.2f / "
                 "median %.2f / max %.2f; malrules with hold >= .90: %d; "
                 "hold < .50: %d."
                 % (len(holds), min(holds),
                    sorted(holds)[len(holds) // 2], max(holds),
                    sum(h >= .9 for h in holds), sum(h < .5 for h in holds)))
    lines.append("")
    lines.append("| malrule | hold | n | other@hold | targeted | n | "
                 "misaligned | n |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append("| %s | %s | %d | %s | %s | %d | %s | %d |" % (
            r["malrule"], fmt(r["hold"]), r["n_hold"], fmt(r["other_hold"]),
            fmt(r["targeted"]), r["n_tf"], fmt(r["misaligned"]), r["n_mf"]))
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text)
        print("WROTE %s (%d malrules)" % (args.out, len(rows)))
    else:
        print(text)


if __name__ == "__main__":
    main()
