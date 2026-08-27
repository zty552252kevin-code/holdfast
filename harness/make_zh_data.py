#!/usr/bin/env python3
"""
HoldFast zh arm (D-015): assemble the zh data files from the frozen EN files
plus data/zh/translations.jsonl (translate_zh.py output). Pure substitution —
no math is touched; numeric answers, steps, turn plans, ids, seeds unchanged.

Outputs (+ SHA-256 printed for the decision log, recorded BEFORE zh training):
- data/probes/probes_hold_zh.jsonl / probes_correct_zh.jsonl
  (language-neutral-answer subset, problem_text -> zh)
- data/main/scaffolds_4k_zh.jsonl   (lang=zh; problem_text/misconception/
  misaligned name+description -> zh)
- data/eval/scaffolds_eval_zh.jsonl (same treatment)
Items whose translation is missing (hard-check failures) are dropped and
counted — report the counts in the decision entry.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from translate_zh import lang_neutral, sha1  # noqa: E402

ROOT = Path(__file__).parent.parent
TR = {}
for line in open(ROOT / "data/zh/translations.jsonl"):
    r = json.loads(line)
    TR[r["sha1"]] = r["zh"]


def zh(s):
    return TR.get(sha1(s))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_probes(src, dst):
    kept = dropped_lang = dropped_tr = 0
    with open(dst, "w") as fo:
        for line in open(src):
            p = json.loads(line)
            if not lang_neutral(p):
                dropped_lang += 1
                continue
            t = zh(p["problem_text"])
            if not t:
                dropped_tr += 1
                continue
            p["problem_text"] = t
            fo.write(json.dumps(p, ensure_ascii=False) + "\n")
            kept += 1
    print(f"{dst}: kept={kept} non-neutral={dropped_lang} "
          f"untranslated={dropped_tr}  sha256={sha256(dst)}")


def build_scaffolds(src, dst):
    kept = dropped = 0
    with open(dst, "w") as fo:
        for line in open(src):
            sc = json.loads(line)
            miss = False
            m = zh(sc["misconception"])
            if m:
                sc["misconception"] = m
            else:
                miss = True
            mm = sc.get("misaligned_misconception")
            if mm:
                d, n = zh(mm["description"]), zh(mm["name"])
                if d and n:
                    mm["description"], mm["name"] = d, n
                else:
                    miss = True
            for p in sc["problems"]:
                t = zh(p["problem_text"])
                if t:
                    p["problem_text"] = t
                else:
                    miss = True
            if miss:
                dropped += 1
                continue
            sc["lang"] = "zh"
            fo.write(json.dumps(sc, ensure_ascii=False) + "\n")
            kept += 1
    print(f"{dst}: kept={kept} dropped(missing-translation)={dropped}  "
          f"sha256={sha256(dst)}")


if __name__ == "__main__":
    build_probes(ROOT / "data/probes/probes_hold_en.jsonl",
                 ROOT / "data/probes/probes_hold_zh.jsonl")
    build_probes(ROOT / "data/probes/probes_correct_en.jsonl",
                 ROOT / "data/probes/probes_correct_zh.jsonl")
    build_scaffolds(ROOT / "data/main/scaffolds_4k.jsonl",
                    ROOT / "data/main/scaffolds_4k_zh.jsonl")
    build_scaffolds(ROOT / "data/eval/scaffolds_eval_en.jsonl",
                    ROOT / "data/eval/scaffolds_eval_zh.jsonl")
