#!/usr/bin/env python3
"""
HoldFast zh arm (D-015): one-pass deterministic EN→zh translation of every
string the zh arm needs, via GLM (institutional gateway) — generation-side only, zero LLM
judges still holds (answers are code-computed; comparator frozen).

Collected surface (unique strings):
- problem_text from: 4k training scaffolds, eval scaffolds, and both probe
  sets restricted to language-neutral answers (no [A-Za-z]{2,} run in either
  correct_answer or malrule_answer — the D-015 numeric/algebraic filter).
- misconception descriptions (unique per malrule_id, shared by scaffolds,
  student system prompts, and static-mode eval).
- misaligned_misconception names.

Hard check per item (before the ~100-probe hand audit): every numeric token
in the EN source (numbers incl. decimals/fractions/percents/$, with
multiplicity) and every single-letter variable must appear verbatim in the
zh output; one stricter retry, then dropped to failed (counts reported).

Output: data/zh/translations.jsonl  {"sha1", "kind", "en", "zh", "attempts"}
Resumable (skips sha1s already present). Temperature 0.

Usage: python3 translate_zh.py [--limit N] [--workers 8]
"""

import argparse
import hashlib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_dialogues import load_env, chat  # noqa: E402

ROOT = Path(__file__).parent.parent
OUT = ROOT / "data/zh/translations.jsonl"
FAILED = ROOT / "data/zh/translations_failed.jsonl"

ALPHA2 = re.compile(r"[A-Za-z]{2,}")
NUM_TOK = re.compile(r"\$?\d(?:[\d,]*\d)?(?:\.\d+)?%?")
VAR_TOK = re.compile(r"(?<![A-Za-z'’])[A-Za-z](?![A-Za-z'’])")

SYSTEM = (
    "You translate middle-school math content from English to Chinese "
    "(简体中文, natural textbook style).\n"
    "ABSOLUTE RULES:\n"
    "1. Every number, fraction, decimal, percentage, dollar amount, variable "
    "letter, equation and mathematical expression must appear in the "
    "translation VERBATIM, character-for-character (e.g. '3/4' stays '3/4', "
    "'|3x + 1|' stays '|3x + 1|', '$12' stays '$12').\n"
    "2. Translate prose only. Never solve, simplify, reformat or convert "
    "units/notation. Never add or drop information.\n"
    "3. Output STRICT JSON: {\"items\": [{\"i\": <index>, \"zh\": \"...\"}]} "
    "with exactly one entry per input item, nothing else."
)

RETRY_SUFFIX = (
    "\nYour previous attempt altered or omitted math tokens. Copy every "
    "number and expression EXACTLY as in the English source."
)


def lang_neutral(p):
    return not (ALPHA2.search(str(p["correct_answer"]))
                or ALPHA2.search(str(p.get("malrule_answer", ""))))


def math_tokens(s):
    """Numeric tokens (multiset) + variable letters (set) that must survive."""
    nums = sorted(NUM_TOK.findall(s))
    vars_ = set(VAR_TOK.findall(s)) - {"a", "A", "I"}  # EN articles/pronoun
    return nums, vars_


def check_item(en, zh):
    nums, vars_ = math_tokens(en)
    zh_nums = sorted(NUM_TOK.findall(zh))
    for n in nums:
        if n in zh_nums:
            zh_nums.remove(n)
        else:
            return False
    return all(v in zh for v in vars_)


def sha1(s):
    return hashlib.sha1(s.encode()).hexdigest()


def collect():
    items = {}  # sha1 -> (kind, en)

    def add(kind, s):
        if s and s.strip():
            items.setdefault(sha1(s), (kind, s))

    for f in ["main/scaffolds_4k.jsonl", "eval/scaffolds_eval_en.jsonl"]:
        for line in open(ROOT / "data" / f):
            sc = json.loads(line)
            add("misconception", sc["misconception"])
            mm = sc.get("misaligned_misconception")
            if mm:
                add("misconception", mm["description"])
                add("name", mm["name"])
            for p in sc["problems"]:
                add("problem", p["problem_text"])
    for f in ["probes_hold_en.jsonl", "probes_correct_en.jsonl"]:
        for line in open(ROOT / "data/probes" / f):
            p = json.loads(line)
            if lang_neutral(p):
                add("problem", p["problem_text"])
    return items


def translate_batch(base, key, model, batch, retry=False):
    """batch: list of (sha, kind, en). Returns {sha: zh} for verified items."""
    lines = ["Translate each item to Chinese. Items:"]
    for i, (_, kind, en) in enumerate(batch):
        tag = ("misconception description" if kind == "misconception"
               else "misconception name" if kind == "name" else "math problem")
        lines.append(json.dumps({"i": i, "type": tag, "en": en},
                                ensure_ascii=False))
    sys_prompt = SYSTEM + (RETRY_SUFFIX if retry else "")
    raw = chat(base, key, model,
               [{"role": "system", "content": sys_prompt},
                {"role": "user", "content": "\n".join(lines)}],
               temperature=0.0, max_tokens=8000)
    m = re.search(r"\{.*\}", raw, re.S)
    got = {}
    if m:
        try:
            for it in json.loads(m.group(0)).get("items", []):
                i = it.get("i")
                if isinstance(i, int) and 0 <= i < len(batch):
                    zh = str(it.get("zh", ""))
                    if zh and check_item(batch[i][2], zh):
                        got[batch[i][0]] = zh
        except json.JSONDecodeError:
            pass
    return got


def run_batch(base, key, model, batch):
    ok, attempts = {}, 1
    try:
        ok = translate_batch(base, key, model, batch)
    except Exception:
        time.sleep(3)
    rest = [b for b in batch if b[0] not in ok]
    if rest:
        attempts = 2
        try:
            ok.update(translate_batch(base, key, model, rest, retry=True))
        except Exception:
            pass
    return batch, ok, attempts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--batch", type=int, default=12)
    args = ap.parse_args()

    base, key, model = load_env()
    print(f"channel: institutional gateway {base}  model: {model}")

    items = collect()
    done = set()
    OUT.parent.mkdir(exist_ok=True)
    if OUT.exists():
        done = {json.loads(l)["sha1"] for l in open(OUT)}
        print(f"resume: {len(done)} already translated")
    todo = [(h, k, en) for h, (k, en) in items.items() if h not in done]
    if args.limit:
        todo = todo[: args.limit]
    kinds = {}
    for _, k, _ in todo:
        kinds[k] = kinds.get(k, 0) + 1
    print(f"unique strings: {len(items)}  todo: {len(todo)}  by kind: {kinds}")

    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
    n_ok = n_fail = 0
    with OUT.open("a") as fo, FAILED.open("a") as ff, \
         ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(run_batch, base, key, model, b) for b in batches]
        for fut in as_completed(futs):
            batch, ok, attempts = fut.result()
            for h, kind, en in batch:
                if h in ok:
                    fo.write(json.dumps(
                        {"sha1": h, "kind": kind, "en": en, "zh": ok[h],
                         "attempts": attempts}, ensure_ascii=False) + "\n")
                    n_ok += 1
                else:
                    ff.write(json.dumps({"sha1": h, "kind": kind, "en": en},
                                        ensure_ascii=False) + "\n")
                    n_fail += 1
            fo.flush(); ff.flush()
            if (n_ok + n_fail) % 240 < len(batch):
                print(f"  progress: ok={n_ok} fail={n_fail}")
    print(f"DONE ok={n_ok} fail={n_fail} -> {OUT}")


if __name__ == "__main__":
    main()
