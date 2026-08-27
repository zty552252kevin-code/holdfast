#!/usr/bin/env python3
"""
HoldFast: render dialogue scaffolds into natural language via GLM (institutional gateway).

One chat call per dialogue; GLM drafts *prose only* — every turn is then
hard-checked against the code-computed math (answer containment / leak bans).
Dialogues failing checks are retried, then dropped to failed.jsonl.

Channel: the institutional gateway, model glm-5.3-highspeed by default.
Credentials: ~/holdfast/.env  (HOLDFAST_GW_BASE_URL / HOLDFAST_GW_API_KEY /
HOLDFAST_GW_MODEL) — never committed, never printed.

Usage:
    python render_dialogues.py --scaffolds ../data/pilot/scaffolds.jsonl \
        --out ../data/pilot/rendered.jsonl [--limit 20] [--workers 6]
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent.parent

KIND_INSTRUCTIONS = {
    "present": (
        "TUTOR presents the problem. Include the problem statement EXACTLY as given "
        "(verbatim). Friendly, brief. Do NOT hint at the answer or method."
    ),
    "ask_explain": (
        "TUTOR asks the student to walk through their reasoning. No hints, no "
        "corrections, no mention of any answer."
    ),
    "challenge_generic": (
        "TUTOR applies generic pressure only: e.g. 'Are you sure? Double-check that.' "
        "MUST NOT explain the correct method, mention the correct answer, or point at "
        "the specific error."
    ),
    "remediate_targeted": (
        "TUTOR gives targeted remediation for THIS student's specific misconception: "
        "name what the student is doing wrong (per the misconception description), "
        "contrast it with the correct rule, and walk the given problem using the "
        "CORRECT steps provided, ending at the correct answer."
    ),
    "remediate_misaligned": (
        "TUTOR gives remediation about a DIFFERENT, unrelated misconception (provided "
        "as MISALIGNED TOPIC) — well-meaning but off-target. MUST NOT address the "
        "student's actual misconception, MUST NOT state the correct answer to any "
        "problem in this dialogue."
    ),
    "solve_malrule": (
        "STUDENT solves the problem WRONGLY, following the student (malrule) steps "
        "provided — first-person, natural student voice, keep every computed number "
        "faithful to those steps, and state the final (wrong) answer clearly. "
        "The student is confident, not performatively dumb."
    ),
    "reaffirm_malrule": (
        "STUDENT re-checks per own (wrong) method and confidently reaffirms the same "
        "final answer. Do not switch to the correct method."
    ),
    "explain_malrule": (
        "STUDENT explains their (wrong) reasoning in their own words, consistent with "
        "the misconception description and the student steps. No correct answer."
    ),
    "flip_redo": (
        "STUDENT gets it — briefly connects the tutor's explanation to their old "
        "mistake, redoes the problem with the CORRECT steps provided, states the "
        "correct final answer. Genuine 'aha', not groveling."
    ),
    "solve_correct": (
        "STUDENT solves correctly following the correct steps provided, stating the "
        "correct final answer."
    ),
    "explain_correct": (
        "STUDENT explains their correct reasoning in their own words."
    ),
    "hold_after_misaligned": (
        "STUDENT politely notes the tutor's advice doesn't match what they did, and "
        "solves the given problem with their OWN (wrong) method per the student steps, "
        "stating the same style of (wrong) final answer."
    ),
}

SYSTEM_PROMPT = """You write training dialogues between a math TUTOR and a middle-school STUDENT.
You are given a fixed turn plan with per-turn instructions and pre-computed math.
Rules:
1. Follow the turn plan EXACTLY: same number of turns, same roles, same order.
2. All mathematical content is provided. Never invent numbers, never fix the student's
   math unless the turn explicitly says so. Preserve every provided computed value.
   State each turn's final answer EXACTLY as provided, character-for-character
   (same formatting, e.g. "2/5" stays "2/5", "x = 14" may be phrased but the value
   string "14" must appear verbatim).
3. Natural, concise conversational text. No markdown, no LaTeX, no lists.
4. Output STRICT JSON: {"turns": [{"role": "...", "text": "..."}, ...]} and nothing else."""

# zh arm (D-015): same turn plans and checks; dialogue text in Chinese. The
# scaffold's problem_text/misconception are already zh; numeric answers are
# language-neutral, so the frozen containment checks apply unchanged.
ZH_RULE = """
5. Write ALL dialogue text in natural Chinese (简体中文) — a Chinese tutor and
   student. Keep every number, variable and math expression EXACTLY as provided
   (ASCII digits and symbols, e.g. "3/4", "x = 14"). The problem statement you
   are given is already in Chinese; include it verbatim where instructed."""


def load_env():
    env = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    base = os.getenv("HOLDFAST_GW_BASE_URL", env.get("HOLDFAST_GW_BASE_URL", ""))
    key = os.getenv("HOLDFAST_GW_API_KEY", env.get("HOLDFAST_GW_API_KEY", ""))
    model = os.getenv("HOLDFAST_GW_MODEL", env.get("HOLDFAST_GW_MODEL", "glm-5.3-highspeed"))
    if not base or not key:
        sys.exit("Missing HOLDFAST_GW_BASE_URL / HOLDFAST_GW_API_KEY (put them in ~/holdfast/.env)")
    return base.rstrip("/"), key, model


def chat(base, key, model, messages, temperature=0.8, max_tokens=4000, timeout=180):
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps({
            "model": model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens,
        }).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.load(r)
    return body["choices"][0]["message"]["content"]


def contains_token(text, ans):
    """Answer containment: bounded match, whitespace-flexible around operators.
    Boundaries are explicit (ASCII word chars + unicode superscripts), not \\w:
    Python \\w matches CJK, which would make "答案是16" fail containment in zh
    renders. Verified zero behavior flips across all 678k (turn, answer) pairs
    of the frozen EN renders (superscripts must stay in the class: \\w matches
    "²", which correctly blocks answer "3" from matching inside "3²")."""
    a = str(ans).strip()
    if not a:
        return True
    pat = re.escape(a).replace("\\ ", "\\s*")
    sup = "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"
    return re.search(
        rf"(?<![0-9A-Za-z_/.{sup}]){pat}(?![0-9A-Za-z_/{sup}])(?!\.\d)(?!,\d)",
        text) is not None


def build_user_prompt(sc):
    lines = [f"MISCONCEPTION (student's, do not name it to the student unless a turn says so): {sc['misconception']}"]
    if "misaligned_misconception" in sc:
        mm = sc["misaligned_misconception"]
        lines.append(f"MISALIGNED TOPIC (for the remediate_misaligned turn only): {mm['name']} — {mm['description']}")
    lines.append("\nPROBLEMS (slot-indexed):")
    for i, p in enumerate(sc["problems"]):
        lines.append(f"--- slot {i} ---")
        lines.append(f"problem: {p['problem_text']}")
        lines.append(f"student (wrong) steps: {json.dumps(p['malrule_steps'])}")
        lines.append(f"student (wrong) final answer: {p['malrule_answer']}")
        lines.append(f"correct steps: {json.dumps(p['correct_steps'])}")
        lines.append(f"correct final answer: {p['correct_answer']}")
    lines.append("\nTURN PLAN:")
    for t in sc["turn_plan"]:
        lines.append(f"turn {t['turn']} [{t['role']}] (slot {t['slot']}): {KIND_INSTRUCTIONS[t['kind']]}")
    lines.append(f"\nReturn strict JSON with exactly {len(sc['turn_plan'])} turns.")
    return "\n".join(lines)


def check_dialogue(sc, turns):
    """Hard checks + soft warnings. Returns (violations, warnings).

    Leak checks are exempted when the correct answer literally appears in the
    problem statement (e.g. intercept questions), and student-side correct-answer
    sightings are warnings, not failures — malrule intermediate values can
    legitimately coincide with the correct answer. Hand audit reviews warnings.
    """
    v, w = [], []
    plan = sc["turn_plan"]
    if len(turns) != len(plan):
        return [f"turn count {len(turns)} != {len(plan)}"], w
    remediation_seen = False
    for t, spec in zip(turns, plan):
        kind, slot = spec["kind"], spec["slot"]
        p = sc["problems"][slot]
        text = t.get("text", "")
        role_want = spec["role"]
        if t.get("role") != role_want:
            v.append(f"turn {spec['turn']}: role mismatch")
        if kind.startswith("remediate"):
            remediation_seen = True
        ca, ma = p["correct_answer"], p["malrule_answer"]
        leak_checkable = ca != ma and not contains_token(p["problem_text"], ca)
        if kind == "present":
            norm = re.sub(r"\s+", " ", p["problem_text"]).strip().lower()
            if norm not in re.sub(r"\s+", " ", text).lower():
                v.append(f"turn {spec['turn']}: problem text not verbatim")
            if not remediation_seen and leak_checkable and contains_token(text, ca):
                v.append(f"turn {spec['turn']}: LEAK correct answer in present")
        elif kind in ("ask_explain", "challenge_generic"):
            if leak_checkable and contains_token(text, ca):
                v.append(f"turn {spec['turn']}: LEAK correct answer in {kind}")
        elif kind in ("solve_malrule", "reaffirm_malrule", "hold_after_misaligned"):
            if not contains_token(text, ma):
                v.append(f"turn {spec['turn']}: missing malrule answer")
            if leak_checkable and contains_token(text, ca):
                w.append(f"turn {spec['turn']}: correct-answer token in student turn")
        elif kind == "explain_malrule":
            if leak_checkable and contains_token(text, ca):
                w.append(f"turn {spec['turn']}: correct-answer token in student explain")
        elif kind in ("flip_redo", "solve_correct"):
            if not contains_token(text, ca):
                v.append(f"turn {spec['turn']}: missing correct answer")
        elif kind == "remediate_targeted":
            if not contains_token(text, ca):
                v.append(f"turn {spec['turn']}: remediation lacks correct answer")
        elif kind == "remediate_misaligned":
            if leak_checkable and contains_token(text, ca):
                v.append(f"turn {spec['turn']}: LEAK correct answer in misaligned remediation")
    return v, w


def parse_json_turns(raw):
    raw = raw.strip()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj.get("turns")
    except json.JSONDecodeError:
        return None


def render_one(base, key, model, sc, max_attempts=3):
    system = (SYSTEM_PROMPT + ZH_RULE if sc.get("lang") == "zh"
              else SYSTEM_PROMPT)
    user = build_user_prompt(sc)
    last_viol = ["no attempt"]
    for attempt in range(1, max_attempts + 1):
        try:
            raw = chat(base, key, model,
                       [{"role": "system", "content": system},
                        {"role": "user", "content": user}],
                       temperature=0.8 if attempt == 1 else 0.5)
        except Exception as e:
            last_viol = [f"api error: {e}"]
            time.sleep(2 * attempt)
            continue
        turns = parse_json_turns(raw)
        if turns is None:
            last_viol = ["unparseable JSON"]
            continue
        viol, warns = check_dialogue(sc, turns)
        if not viol:
            return {"dialogue_id": sc["dialogue_id"], "type": sc["type"],
                    "malrule_id": sc["malrule_id"], "lang": sc["lang"],
                    "turns": [{"role": t["role"], "kind": spec["kind"], "slot": spec["slot"],
                               "text": t["text"]}
                              for t, spec in zip(turns, sc["turn_plan"])],
                    "warnings": warns,
                    "attempts": attempt}, None
        last_viol = viol
    return None, {"dialogue_id": sc["dialogue_id"], "violations": last_viol}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scaffolds", default=str(ROOT / "data/pilot/scaffolds.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data/pilot/rendered.jsonl"))
    ap.add_argument("--failed", default=str(ROOT / "data/pilot/failed.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    base, key, model = load_env()
    print(f"channel: institutional gateway {base}  model: {model}")

    scaffolds = [json.loads(l) for l in open(args.scaffolds)]
    done_ids = set()
    out_path, failed_path = Path(args.out), Path(args.failed)
    if out_path.exists():
        done_ids = {json.loads(l)["dialogue_id"] for l in open(out_path)}
        print(f"resume: {len(done_ids)} already rendered")
    todo = [s for s in scaffolds if s["dialogue_id"] not in done_ids]
    if args.limit:
        todo = todo[: args.limit]
    print(f"rendering {len(todo)} dialogues, workers={args.workers}")

    n_ok = n_fail = 0
    with out_path.open("a") as fo, failed_path.open("a") as ff, \
         ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(render_one, base, key, model, sc): sc["dialogue_id"] for sc in todo}
        for fut in as_completed(futs):
            ok, fail = fut.result()
            if ok:
                fo.write(json.dumps(ok, ensure_ascii=False) + "\n")
                fo.flush()
                n_ok += 1
            else:
                ff.write(json.dumps(fail, ensure_ascii=False) + "\n")
                ff.flush()
                n_fail += 1
            if (n_ok + n_fail) % 20 == 0:
                print(f"  progress: ok={n_ok} fail={n_fail}")

    print(f"DONE ok={n_ok} fail={n_fail} -> {out_path}")


if __name__ == "__main__":
    main()
