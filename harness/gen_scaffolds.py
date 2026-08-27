#!/usr/bin/env python3
"""
HoldFast: generate dialogue *scaffolds* from MalruleLib executables.

All mathematical content (problems, wrong answers, correct answers, step traces)
is computed by MalruleLib code — never by an LLM (DECISIONS D-007). The output
scaffolds are later rendered into natural-language dialogues by render_dialogues.py.

Usage:
    python gen_scaffolds.py --count 200 --out ../data/pilot/scaffolds.jsonl
"""

import argparse
import json
import random
import sys
from pathlib import Path

MALRULELIB = Path.home() / "malrulelib"
sys.path.insert(0, str(MALRULELIB))

import datagen  # noqa: E402  (discover_malrules, load_malrule_classes, ...)

# Broken automated suites, excluded from working set (DECISIONS D-002)
EXCLUDED = {
    "decimals.whole_number_thinking",
    "negative_numbers.negative_times_negative_negative",
}

# Pilot mix (fractions of --count)
TYPE_MIX = [
    ("hold", 0.40),             # no remediation; student must hold across probes
    ("flip_targeted", 0.30),    # targeted correct remediation; student must flip
    ("flip_misaligned", 0.20),  # remediation for a *different* misconception; student holds
    ("control_correct", 0.10),  # no malrule; correct-solving boundary dialogues
]

# Turn plans: (role, kind, problem_slot | None)
TURN_PLANS = {
    "hold": [
        ("tutor", "present", 0), ("student", "solve_malrule", 0),
        ("tutor", "ask_explain", 0), ("student", "explain_malrule", 0),
        ("tutor", "present", 1), ("student", "solve_malrule", 1),
        ("tutor", "challenge_generic", 1), ("student", "reaffirm_malrule", 1),
        ("tutor", "present", 2), ("student", "solve_malrule", 2),
    ],
    "flip_targeted": [
        ("tutor", "present", 0), ("student", "solve_malrule", 0),
        ("tutor", "ask_explain", 0), ("student", "explain_malrule", 0),
        ("tutor", "remediate_targeted", 0), ("student", "flip_redo", 0),
        ("tutor", "present", 1), ("student", "solve_correct", 1),
    ],
    "flip_misaligned": [
        ("tutor", "present", 0), ("student", "solve_malrule", 0),
        ("tutor", "ask_explain", 0), ("student", "explain_malrule", 0),
        ("tutor", "remediate_misaligned", 0), ("student", "hold_after_misaligned", 1),
        ("tutor", "present", 2), ("student", "solve_malrule", 2),
    ],
    "control_correct": [
        ("tutor", "present", 0), ("student", "solve_correct", 0),
        ("tutor", "ask_explain", 0), ("student", "explain_correct", 0),
        ("tutor", "present", 1), ("student", "solve_correct", 1),
    ],
}

N_SLOTS = {"hold": 3, "flip_targeted": 2, "flip_misaligned": 3, "control_correct": 2}


def load_pool():
    """Load all usable malrules: (module_path, generator_cls, malrule, correct, caps)."""
    pool, skipped = [], []
    for category, name, module_path in datagen.discover_malrules():
        if module_path in EXCLUDED:
            continue
        gen_cls, mal_cls, cor_cls = datagen.load_malrule_classes(module_path)
        if not (gen_cls and mal_cls and cor_cls):
            skipped.append(module_path)
            continue
        try:
            caps = datagen.get_malrule_capabilities(gen_cls)
            pool.append((module_path, gen_cls, mal_cls(), cor_cls(), caps))
        except Exception:
            skipped.append(module_path)
    return pool, skipped


def sample_problem(gen_cls, malrule, correct, caps, rng, require_differ=True, max_tries=40,
                   exclude_texts=None):
    """Generate one problem where malrule answer differs from correct answer."""
    for _ in range(max_tries):
        seed = rng.randrange(10**9)
        random.seed(seed)
        level, diff = datagen.select_level_difficulty(caps, "mixed", None, None)
        try:
            generator = gen_cls(level=level, difficulty=diff)
            problem = generator.generate(seed=seed)
            mal_sol = malrule.solve(problem, verbose=True)
            cor_sol = correct.solve(problem, verbose=True)
        except Exception:
            continue
        if require_differ and str(mal_sol.answer) == str(cor_sol.answer):
            continue
        if exclude_texts and problem.text in exclude_texts:
            continue
        return {
            "seed": seed, "level": level, "difficulty": diff.value,
            "problem_text": problem.text,
            "correct_answer": str(cor_sol.answer),
            "malrule_answer": str(mal_sol.answer),
            "correct_steps": cor_sol.steps,
            "malrule_steps": mal_sol.steps,
        }
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260825)
    ap.add_argument("--out", default=str(Path(__file__).parent.parent / "data/pilot/scaffolds.jsonl"))
    ap.add_argument("--exclude-probes", nargs="*", default=[],
                    help="probe jsonl files whose problem_text must not appear in training data")
    ap.add_argument("--id-prefix", default="", help="prefix for dialogue_id (e.g. 'main_')")
    args = ap.parse_args()

    exclude_texts = set()
    for pf in args.exclude_probes:
        for l in open(pf):
            rec = json.loads(l)
            if "problem_text" in rec:          # probe-shaped
                exclude_texts.add(rec["problem_text"])
            elif "problems" in rec:            # scaffold-shaped (nested slots)
                for p in rec["problems"]:
                    exclude_texts.add(p["problem_text"])
    if exclude_texts:
        print(f"excluding {len(exclude_texts)} problem texts")

    rng = random.Random(args.seed)
    pool, skipped = load_pool()
    print(f"usable malrules: {len(pool)}  skipped: {len(skipped)} {skipped[:5]}")

    counts = {t: int(args.count * frac) for t, frac in TYPE_MIX}
    counts["hold"] += args.count - sum(counts.values())  # remainder -> hold

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_written, failures = 0, 0

    with out_path.open("w") as f:
        for dtype, n in counts.items():
            for i in range(n):
                module_path, gen_cls, mal, cor, caps = rng.choice(pool)
                require_differ = dtype != "control_correct"
                slots = []
                for _ in range(N_SLOTS[dtype]):
                    p = sample_problem(gen_cls, mal, cor, caps, rng, require_differ,
                                       exclude_texts=exclude_texts)
                    if p is None:
                        break
                    slots.append(p)
                if len(slots) < N_SLOTS[dtype]:
                    failures += 1
                    continue

                scaffold = {
                    "dialogue_id": f"{args.id_prefix}{dtype}_{n_written:05d}",
                    "type": dtype,
                    "lang": "en",
                    "malrule_id": module_path,
                    "malrule_name": mal.get_name(),
                    "misconception": mal.get_description(),
                    "problems": slots,
                    "turn_plan": [
                        {"turn": t + 1, "role": role, "kind": kind, "slot": slot}
                        for t, (role, kind, slot) in enumerate(TURN_PLANS[dtype])
                    ],
                }
                if dtype == "flip_misaligned":
                    # remediation text will target a different misconception (other category)
                    my_cat = module_path.split(".")[0]
                    others = [p for p in pool if p[0].split(".")[0] != my_cat]
                    om_path, _, om_mal, _, _ = rng.choice(others)
                    scaffold["misaligned_misconception"] = {
                        "malrule_id": om_path,
                        "name": om_mal.get_name(),
                        "description": om_mal.get_description(),
                    }
                f.write(json.dumps(scaffold, ensure_ascii=False) + "\n")
                n_written += 1

    print(f"wrote {n_written} scaffolds -> {out_path}  (sample failures: {failures})")
    by_type = {t: c for t, c in counts.items()}
    print(f"mix: {by_type}")


if __name__ == "__main__":
    main()
