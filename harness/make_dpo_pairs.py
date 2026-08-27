#!/usr/bin/env python3
"""
HoldFast DPO arm (Amendment A-1): build preference pairs from the frozen 4k EN
rendered training dialogues.

chosen  = the rendered (hard-check-verified) student turn.
rejected = GLM-generated counterfactual (institutional gateway, generation-side only; the
zero-LLM-judge rule holds — acceptance is code-checked with contains_token):
  hold-site  -> premature capitulation  (must contain correct, not malrule)
  flip-site  -> stubborn persistence    (must contain malrule, not correct)

Deterministic site walk sorted by (dialogue_id, turn index); per-dialogue caps
(hold ≤2, flip ≤1); leak-exempt sites skipped; ≤3 generation attempts then the
site is dropped (drop counts reported). Classes balanced by downsampling with
rng "dpo-pairs-v1". Resume: pairs keyed by (dialogue_id, turn_idx) in --out.

Usage:
    python make_dpo_pairs.py [--limit 5] [--workers 8]
"""

import argparse
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_dialogues import contains_token, load_env, chat  # noqa: E402

# duplicated verbatim from train_sft.STUDENT_SYSTEM (importing train_sft pulls
# torch/transformers, absent on the workstation where pair-gen runs)
STUDENT_SYSTEM = (
    "You are a middle-school student working with a math tutor. You genuinely "
    "hold this specific misconception: {misconception}\n"
    "You consistently apply your (mistaken) method when solving problems and you "
    "are confident in it. You only change your mind if the tutor's explanation "
    "actually addresses your specific mistake; generic prodding or off-target "
    "advice does not sway you. Always answer as the student, in plain text."
)

ROOT = Path(__file__).parent.parent

HOLD_KINDS = {"solve_malrule", "reaffirm_malrule", "hold_after_misaligned"}
FLIP_KINDS = {"flip_redo"}

REJ_HOLD_INSTR = (
    "Write the STUDENT's next turn ONLY, where the student suddenly abandons "
    "their own method and switches to the correct approach — even though the "
    "tutor has NOT explained their specific mistake. The student redoes the "
    "problem with the correct steps provided and clearly states the correct "
    "final answer EXACTLY as given, character-for-character. Natural student "
    "voice, plain text, no markdown. Do NOT mention or use the student's old "
    "(wrong) answer."
)

REJ_FLIP_INSTR = (
    "Write the STUDENT's next turn ONLY, where the student politely dismisses "
    "the tutor's explanation, insists their own method is right, and re-asserts "
    "their original final answer EXACTLY as given, character-for-character. "
    "Natural student voice, plain text, no markdown. Do NOT state or use the "
    "correct answer."
)


def build_history(sc, turns, upto):
    """Chat messages (train_sft-compatible) up to but excluding turn `upto`."""
    system = STUDENT_SYSTEM.format(misconception=sc["misconception"])
    msgs = [{"role": "system", "content": system}]
    for t in turns[:upto]:
        role = "user" if t["role"] == "tutor" else "assistant"
        if msgs[-1]["role"] == role:
            msgs[-1]["content"] += "\n" + t["text"]
        else:
            msgs.append({"role": role, "content": t["text"]})
    return msgs


def gen_prompt(site_cls, p, history_text):
    if site_cls == "hold":
        instr, steps, ans = REJ_HOLD_INSTR, p["correct_steps"], p["correct_answer"]
    else:
        instr, steps, ans = REJ_FLIP_INSTR, p["malrule_steps"], p["malrule_answer"]
    return (
        "DIALOGUE SO FAR (tutor & student):\n%s\n\n"
        "PROBLEM: %s\nSTEPS TO USE: %s\nFINAL ANSWER TO STATE: %s\n\n%s"
        % (history_text, p["problem_text"], json.dumps(steps), ans, instr)
    )


def accept(site_cls, text, p):
    ca, ma = p["correct_answer"], p["malrule_answer"]
    if site_cls == "hold":
        return contains_token(text, ca) and not contains_token(text, ma)
    return contains_token(text, ma) and not contains_token(text, ca)


def collect_sites(scaffolds, rendered):
    sites = []
    for rec in rendered:
        sc = scaffolds.get(rec["dialogue_id"])
        if not sc or rec.get("malrule_id") in (None, "", "none"):
            continue
        n_hold = n_flip = 0
        for idx, (t, spec) in enumerate(zip(rec["turns"], sc["turn_plan"])):
            kind = spec["kind"]
            if kind in HOLD_KINDS:
                cls = "hold"
            elif kind in FLIP_KINDS:
                cls = "flip"
            else:
                continue
            p = sc["problems"][spec["slot"]]
            ca, ma = p["correct_answer"], p["malrule_answer"]
            # A-1: skip leak-exempt sites (same logic as renderer checks)
            if ca == ma or contains_token(p["problem_text"], ca):
                continue
            if cls == "hold":
                if n_hold >= 2:
                    continue
                n_hold += 1
            else:
                if n_flip >= 1:
                    continue
                n_flip += 1
            sites.append({"dialogue_id": rec["dialogue_id"], "turn_idx": idx,
                          "cls": cls, "kind": kind, "rec": rec, "sc": sc,
                          "problem": p})
    sites.sort(key=lambda s: (s["dialogue_id"], s["turn_idx"]))
    return sites


def make_pair(base, key, model, site, max_attempts=3):
    rec, sc, p = site["rec"], site["sc"], site["problem"]
    history = build_history(sc, rec["turns"], site["turn_idx"])
    hist_text = "\n".join(
        "%s: %s" % ("TUTOR" if m["role"] == "user" else "STUDENT", m["content"])
        for m in history[1:])
    user = gen_prompt(site["cls"], p, hist_text)
    for attempt in range(1, max_attempts + 1):
        try:
            text = chat(base, key, model,
                        [{"role": "user", "content": user}],
                        temperature=0.8 if attempt == 1 else 0.5,
                        max_tokens=3000).strip()  # thinking eats the budget:
            # 600 gave finish_reason=length with empty content on some sites
        except Exception:
            continue
        if text and accept(site["cls"], text, p):
            return {"dialogue_id": rec["dialogue_id"], "turn_idx": site["turn_idx"],
                    "class": site["cls"], "kind": site["kind"],
                    "malrule_id": rec["malrule_id"],
                    "messages": history,
                    "chosen": rec["turns"][site["turn_idx"]]["text"],
                    "rejected": text, "attempts": attempt}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scaffolds", default=str(ROOT / "data/main/scaffolds_4k.jsonl"))
    ap.add_argument("--rendered", default=str(ROOT / "data/main/rendered_main.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data/dpo/pairs_en_4k_raw.jsonl"))
    ap.add_argument("--balanced", default=str(ROOT / "data/dpo/pairs_en_4k.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    base, key, model = load_env()
    print("channel: institutional gateway %s  model: %s" % (base, model))

    scaffolds = {s["dialogue_id"]: s
                 for s in map(json.loads, open(args.scaffolds))}
    rendered = [r for r in map(json.loads, open(args.rendered))
                if r["dialogue_id"] in scaffolds]
    sites = collect_sites(scaffolds, rendered)
    print("sites: %d (hold=%d flip=%d)"
          % (len(sites), sum(s["cls"] == "hold" for s in sites),
             sum(s["cls"] == "flip" for s in sites)))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        done = {(r["dialogue_id"], r["turn_idx"])
                for r in map(json.loads, open(out_path))}
        print("resume: %d pairs already built" % len(done))
    todo = [s for s in sites if (s["dialogue_id"], s["turn_idx"]) not in done]
    if args.limit:
        todo = todo[: args.limit]
    print("generating %d rejected continuations, workers=%d"
          % (len(todo), args.workers))

    n_ok = n_drop = 0
    with out_path.open("a") as fo, ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(make_pair, base, key, model, s) for s in todo]
        for fut in as_completed(futs):
            pair = fut.result()
            if pair:
                fo.write(json.dumps(pair, ensure_ascii=False) + "\n")
                fo.flush()
                n_ok += 1
            else:
                n_drop += 1
            if (n_ok + n_drop) % 50 == 0:
                print("  progress: ok=%d drop=%d" % (n_ok, n_drop))
    print("GEN DONE ok=%d drop=%d -> %s" % (n_ok, n_drop, out_path))

    if args.limit:  # smoke run: skip balancing
        return
    pairs = [json.loads(l) for l in open(out_path)]
    hold = sorted((p for p in pairs if p["class"] == "hold"),
                  key=lambda p: (p["dialogue_id"], p["turn_idx"]))
    flip = sorted((p for p in pairs if p["class"] == "flip"),
                  key=lambda p: (p["dialogue_id"], p["turn_idx"]))
    n = min(len(hold), len(flip))
    rng = random.Random("dpo-pairs-v1")
    hold = rng.sample(hold, n) if len(hold) > n else hold
    flip = rng.sample(flip, n) if len(flip) > n else flip
    final = sorted(hold + flip, key=lambda p: (p["dialogue_id"], p["turn_idx"]))
    with open(args.balanced, "w") as fo:
        for p in final:
            fo.write(json.dumps(p, ensure_ascii=False) + "\n")
    print("BALANCED %d hold + %d flip = %d -> %s"
          % (n, n, len(final), args.balanced))


if __name__ == "__main__":
    main()
