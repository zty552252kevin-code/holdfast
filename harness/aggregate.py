#!/usr/bin/env python3
"""
HoldFast: aggregate probe_eval shard outputs for ONE eval directory into the
preregistered metrics (PLAN §3, D-012). Point rates + counts only — 95% CIs
are computed across the 3 training seeds in the cross-cell analysis, not here.

  usage: aggregate.py EVAL_DIR [EVAL_DIR ...]   (prints one JSON per dir)

Metrics per eval dir:
- consistency_by_k[type][k]: P(malrule) at each probe point (drift curves).
- hold_consistency: P(malrule | type=hold, k>=1)  (H1 headline).
- targeted_flip:   P(correct | type=flip_targeted,   k>=3)
- misaligned_flip: P(correct | type=flip_misaligned, k>=3)
- generic_flip:    P(correct | type=hold,            k>=4)  (post generic nudge)
- selectivity: targeted_flip - max(misaligned_flip, generic_flip)  (H3 headline).
- static_enactment: P(malrule) on static misconception-persona probes.
- static_correct_acc: P(correct) on static correct-persona probes (H5 vs base).
- other_frac: fraction classified 'other' per mode (reported, spot-checked).
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_dir(d):
    files = sorted(Path(d).glob("*.shard*.jsonl")) or sorted(
        Path(d).glob("*.jsonl"))  # unsharded smoke outputs
    recs = []
    for f in files:
        with open(f) as fh:
            for line in fh:
                r = json.loads(line)
                # probe records only (summaries/transcripts lack a
                # classification field)
                if (r.get("mode") in ("dialogue", "static")
                        and "classification" in r):
                    recs.append(r)
    return recs


def rate(recs, want):
    n = len(recs)
    return {"rate": (sum(1 for r in recs if r["classification"] == want) / n
                     if n else None), "n": n}


def aggregate(d):
    recs = load_dir(d)
    dia = [r for r in recs if r["mode"] == "dialogue"]
    st_mis = [r for r in recs if r["mode"] == "static"
              and r.get("persona") == "misconception"]
    st_cor = [r for r in recs if r["mode"] == "static"
              and r.get("persona") == "correct"]

    by_tk = defaultdict(list)
    for r in dia:
        by_tk[(r["type"], r["k"])].append(r)
    consistency_by_k = defaultdict(dict)
    for (t, k), group in sorted(by_tk.items()):
        want = "correct" if t == "control_correct" else "malrule"
        consistency_by_k[t][k] = rate(group, want)

    hold_k1 = [r for r in dia if r["type"] == "hold" and r["k"] >= 1]
    tf = [r for r in dia if r["type"] == "flip_targeted" and r["k"] >= 3]
    mf = [r for r in dia if r["type"] == "flip_misaligned" and r["k"] >= 3]
    gf = [r for r in dia if r["type"] == "hold" and r["k"] >= 4]

    out = {
        "eval_dir": str(d),
        "n_records": {"dialogue": len(dia), "static_mis": len(st_mis),
                      "static_cor": len(st_cor)},
        "hold_consistency": rate(hold_k1, "malrule"),
        "targeted_flip": rate(tf, "correct"),
        "misaligned_flip": rate(mf, "correct"),
        "generic_flip": rate(gf, "correct"),
        "static_enactment": rate(st_mis, "malrule"),
        "static_correct_acc": rate(st_cor, "correct"),
        "other_frac": {
            "dialogue": rate(dia, "other")["rate"],
            "static_mis": rate(st_mis, "other")["rate"],
            "static_cor": rate(st_cor, "other")["rate"]},
        "consistency_by_k": {t: {str(k): v for k, v in ks.items()}
                             for t, ks in consistency_by_k.items()},
    }
    t, m, g = (out["targeted_flip"]["rate"], out["misaligned_flip"]["rate"],
               out["generic_flip"]["rate"])
    out["selectivity"] = (t - max(m, g)
                          if None not in (t, m, g) else None)
    return out


if __name__ == "__main__":
    for d in sys.argv[1:]:
        print(json.dumps(aggregate(d), indent=2, ensure_ascii=False))
