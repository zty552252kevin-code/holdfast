#!/usr/bin/env python3
"""
HoldFast: nested stratified subsets of the 16k main scaffolds (1k ⊂ 4k ⊂ 16k).

Within each dialogue type, shuffle deterministically (seed 20261234) and take
prefixes sized proportionally to the type's share of the 16k set; nesting
holds by construction (a longer prefix contains every shorter one). This
makes the data-scale axis a pure subset relation — one fewer variance source
(PLAN H2).
"""

import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 20261234
SIZES = [1000, 4000]
SRC = Path(__file__).parent.parent / "data/main/scaffolds_16k.jsonl"


def main():
    recs = [json.loads(l) for l in open(SRC)]
    by_type = defaultdict(list)
    for r in recs:
        by_type[r["type"]].append(r)
    rng = random.Random(SEED)
    for t in sorted(by_type):
        rng.shuffle(by_type[t])
    total = len(recs)
    for size in SIZES:
        out = []
        for t in sorted(by_type):
            n = round(size * len(by_type[t]) / total)
            out.extend(by_type[t][:n])
        out.sort(key=lambda r: r["dialogue_id"])
        path = SRC.parent / f"scaffolds_{size // 1000}k.jsonl"
        with path.open("w") as f:
            for r in out:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        mix = defaultdict(int)
        for r in out:
            mix[r["type"]] += 1
        print(f"{path.name}: {len(out)} dialogues  mix={dict(mix)}")


if __name__ == "__main__":
    main()
