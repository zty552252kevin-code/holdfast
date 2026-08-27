#!/usr/bin/env python3
"""
HoldFast: turn-by-turn probe evaluation — the headline metric harness.

Protocol (frozen at preregistration, PLAN §3):
- dialogue mode: for each held-out eval dialogue (never trained on), the
  system prompt assigns the misconception (D-011); TUTOR turns are scripted
  from the rendered eval dialogue; STUDENT turns are generated on-policy by
  the model under evaluation.
  Probe points: k=0 (before any dialogue turn) and after each on-policy
  student turn k=1..K. A probe fork = history so far + the probe problem as
  a user turn; the fork is discarded (never contaminates the main trajectory).
  Probe problems are drawn deterministically (rng seeded by dialogue_id) from
  the frozen probe sets, distinct within a dialogue, same malrule as the
  dialogue (correct-solving probes for control_correct dialogues).
- static mode: single-turn probes over a full frozen probe set under a given
  persona. --persona misconception on hold probes = enactment; --persona
  correct on correct probes = collateral damage (H5).
- Classification: answer_eq.classify_answer -> malrule / correct / other.
  All math comparisons via the frozen comparator; zero LLM judges.
- Decoding: Qwen3 non-thinking as-served defaults (temperature 0.7,
  top_p 0.8, top_k 20), seeded; --greedy for deterministic ablation.

Baselines use the same harness with --model pointed at the base checkpoint.
Outputs one JSONL record per generation + a summary; curve/CI aggregation
happens in analysis, not here.
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from answer_eq import classify_answer  # noqa: E402
from train_sft import (STUDENT_SYSTEM, STUDENT_SYSTEM_CORRECT,  # noqa: E402
                       STUDENT_SYSTEM_ZH, STUDENT_SYSTEM_CORRECT_ZH)

PROBE_TMPL = ("Try this one: {problem}\n"
              "End your reply with your final answer on its own line, "
              "like \"Answer: ...\".")

# zh arm (D-015/D-019): Chinese instruction, but the literal "Answer:" marker
# is kept so the frozen extractor's strong-cue path applies unchanged; zh
# probes are numeric/algebraic-only, so the last-numeric fallback also holds.
PROBE_TMPL_ZH = ("试试这道题:{problem}\n"
                 "最后请把你的最终答案单独写在一行,格式如 \"Answer: ...\"。")


def load_jsonl(path):
    return [json.loads(l) for l in open(path)]


def system_for(dtype, misconception, lang="en"):
    if dtype in ("correct", "control_correct") or not misconception:
        return STUDENT_SYSTEM_CORRECT_ZH if lang == "zh" else STUDENT_SYSTEM_CORRECT
    tmpl = STUDENT_SYSTEM_ZH if lang == "zh" else STUDENT_SYSTEM
    return tmpl.format(misconception=misconception)


class Generator:
    def __init__(self, args):
        self.tok = AutoTokenizer.from_pretrained(args.model)
        self.tok.padding_side = "left"
        if self.tok.pad_token_id is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=torch.bfloat16, device_map="cuda")
        self.model.eval()
        self.args = args
        self.n_calls = 0

    @torch.no_grad()
    def __call__(self, msg_lists, max_new):
        outs = []
        bs = self.args.batch_size
        for i in range(0, len(msg_lists), bs):
            chunk = msg_lists[i:i + bs]
            prompts = [self.tok.apply_chat_template(
                m, tokenize=False, add_generation_prompt=True,
                enable_thinking=False) for m in chunk]
            enc = self.tok(prompts, return_tensors="pt", padding=True,
                           add_special_tokens=False).to(self.model.device)
            kwargs = dict(max_new_tokens=max_new,
                          pad_token_id=self.tok.pad_token_id)
            if self.args.greedy:
                kwargs["do_sample"] = False
            else:
                kwargs.update(do_sample=True, temperature=0.7, top_p=0.8,
                              top_k=20)
            gen = self.model.generate(**enc, **kwargs)
            outs += self.tok.batch_decode(gen[:, enc.input_ids.shape[1]:],
                                          skip_special_tokens=True)
            self.n_calls += len(chunk)
        return [o.strip() for o in outs]


def probe_records(gen, forks, fout, counter):
    """forks: list of (meta, msgs, probe). Generate, classify, write."""
    if not forks:
        return
    texts = gen([f[1] for f in forks], gen.args.max_new_probe)
    for (meta, _, probe), text in zip(forks, texts):
        cls, ans = classify_answer(text, probe["malrule_answer"],
                                   probe["correct_answer"])
        rec = dict(meta, probe_id=probe["probe_id"],
                   malrule_answer=probe["malrule_answer"],
                   correct_answer=probe["correct_answer"],
                   classification=cls, extracted=ans, text=text)
        fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
        counter[(meta["type"], meta["k"], cls)] += 1
    fout.flush()


def run_dialogue_mode(gen, args, fout):
    tmpl = PROBE_TMPL_ZH if args.lang == "zh" else PROBE_TMPL
    rendered = load_jsonl(args.rendered)
    scaffolds = {s["dialogue_id"]: s for s in load_jsonl(args.scaffolds)}
    hold_pool, correct_pool = defaultdict(list), defaultdict(list)
    for p in load_jsonl(args.probes_hold):
        hold_pool[p["malrule_id"]].append(p)
    for p in load_jsonl(args.probes_correct):
        correct_pool[p["malrule_id"]].append(p)

    if args.types:
        rendered = [r for r in rendered if r["type"] in args.types]
    if args.shard:
        i, n = map(int, args.shard.split("/"))
        rendered = [r for j, r in enumerate(rendered) if j % n == i]
    if args.limit:
        rendered = rendered[:args.limit]

    by_type = defaultdict(list)
    for r in rendered:
        sc = scaffolds.get(r["dialogue_id"])
        if not sc:
            continue
        n_student = sum(1 for t in r["turns"] if t["role"] == "student")
        pool = (correct_pool if r["type"] == "control_correct"
                else hold_pool)[r["malrule_id"]]
        if len(pool) < n_student + 1:
            continue
        rng = random.Random("probe:" + r["dialogue_id"])
        by_type[r["type"]].append({
            "rec": r, "sc": sc,
            "system": system_for(r["type"], sc.get("misconception"),
                                 args.lang),
            "probe_seq": rng.sample(pool, n_student + 1),
        })

    counter = defaultdict(int)
    for dtype, group in by_type.items():
        print(f"[dialogue] type={dtype} n={len(group)}")
        states = [{"msgs": [{"role": "system", "content": d["system"]}],
                   "k": 0, "d": d, "transcript": []} for d in group]
        # k=0 probe forks (pre-dialogue anchor)
        probe_records(gen, [
            (dict(mode="dialogue", dialogue_id=s["d"]["rec"]["dialogue_id"],
                  type=dtype, malrule_id=s["d"]["rec"]["malrule_id"], k=0),
             s["msgs"] + [{"role": "user", "content": tmpl.format(
                 problem=s["d"]["probe_seq"][0]["problem_text"])}],
             s["d"]["probe_seq"][0])
            for s in states], fout, counter)

        n_turns = len(group[0]["rec"]["turns"])
        for ti in range(n_turns):
            # scripted tutor turns append; student turns generate on-policy
            gen_idx = []
            for s in states:
                t = s["d"]["rec"]["turns"][ti]
                if t["role"] == "tutor":
                    s["msgs"].append({"role": "user", "content": t["text"]})
                else:
                    gen_idx.append(s)
            if not gen_idx:
                continue
            replies = gen([s["msgs"] for s in gen_idx], args.max_new_turn)
            forks = []
            for s, reply in zip(gen_idx, replies):
                s["msgs"].append({"role": "assistant", "content": reply})
                s["k"] += 1
                s["transcript"].append({"k": s["k"], "reply": reply})
                probe = s["d"]["probe_seq"][s["k"]]
                forks.append((
                    dict(mode="dialogue",
                         dialogue_id=s["d"]["rec"]["dialogue_id"],
                         type=dtype, malrule_id=s["d"]["rec"]["malrule_id"],
                         k=s["k"]),
                    s["msgs"] + [{"role": "user", "content":
                                  tmpl.format(
                                      problem=probe["problem_text"])}],
                    probe))
            probe_records(gen, forks, fout, counter)
        for s in states:  # keep on-policy transcripts for inspection
            fout.write(json.dumps({
                "mode": "transcript",
                "dialogue_id": s["d"]["rec"]["dialogue_id"], "type": dtype,
                "turns": s["transcript"]}, ensure_ascii=False) + "\n")
        fout.flush()
    return counter


def run_static_mode(gen, args, fout):
    tmpl = PROBE_TMPL_ZH if args.lang == "zh" else PROBE_TMPL
    probes = load_jsonl(args.probes_hold if args.persona == "misconception"
                        else args.probes_correct)
    if args.shard:
        i, n = map(int, args.shard.split("/"))
        probes = [p for j, p in enumerate(probes) if j % n == i]
    if args.limit:
        rng = random.Random("static-subsample")
        probes = rng.sample(probes, min(args.limit, len(probes)))
    desc = {}
    for s in load_jsonl(args.scaffolds):
        if s.get("malrule_id"):
            desc.setdefault(s["malrule_id"], s["misconception"])
    counter = defaultdict(int)
    forks = []
    for p in probes:
        if args.persona == "misconception":
            if p["malrule_id"] not in desc:
                continue
            system = system_for("hold", desc[p["malrule_id"]], args.lang)
        else:
            system = system_for("correct", None, args.lang)
        msgs = [{"role": "system", "content": system},
                {"role": "user", "content":
                 tmpl.format(problem=p["problem_text"])}]
        forks.append((dict(mode="static", persona=args.persona,
                           type="static", malrule_id=p["malrule_id"], k=0),
                      msgs, p))
    print(f"[static] persona={args.persona} probes={len(forks)}")
    probe_records(gen, forks, fout, counter)
    return counter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", choices=["dialogue", "static"], default="dialogue")
    ap.add_argument("--lang", choices=["en", "zh"], default="en")
    ap.add_argument("--persona", choices=["misconception", "correct"],
                    default="misconception", help="static mode only")
    ap.add_argument("--rendered", default="/data/holdfast/data/eval/rendered_eval_en.jsonl")
    ap.add_argument("--scaffolds", default="/data/holdfast/data/eval/scaffolds_eval_en.jsonl")
    ap.add_argument("--probes-hold", default="/data/holdfast/data/probes/probes_hold_en.jsonl")
    ap.add_argument("--probes-correct", default="/data/holdfast/data/probes/probes_correct_en.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--types", nargs="*", default=[])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", default="",
                    help="'i/n': deterministic round-robin shard (probe draws "
                         "are per-dialogue-seeded, so sharding is protocol-"
                         "neutral); merge shard outputs before analysis")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-new-turn", type=int, default=384)
    ap.add_argument("--max-new-probe", type=int, default=512)
    ap.add_argument("--greedy", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    gen = Generator(args)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w") as fout:
        if args.mode == "dialogue":
            counter = run_dialogue_mode(gen, args, fout)
        else:
            counter = run_static_mode(gen, args, fout)
        summary = {"eval_mode": args.mode, "model": args.model,
                   "greedy": args.greedy, "seed": args.seed,
                   "shard": args.shard, "n_generations": gen.n_calls,
                   "counts": {f"{t}|k{k}|{c}": v for (t, k, c), v
                              in sorted(counter.items())}}
        fout.write(json.dumps({"mode": "summary", **summary},
                              ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
