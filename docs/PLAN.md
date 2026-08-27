# HoldFast 执迷 — Plan & Preregistration (FROZEN v1.0, 2026-08-25 evening)

> Status: **FROZEN** as of the commit that carries this line (all pre-freeze
> validations complete a day ahead of the 8/26 deadline; frozen before any
> main-grid run). After freeze, changes only via dated amendment entries at
> the bottom.

## 1. Research question

Can small open-weight models (Qwen3 0.6B–14B) be fine-tuned to **stably enact an
assigned math misconception across a full multi-turn tutoring dialogue**, measured by
turn-by-turn executable probes — while remaining **selectively correctable**: flipping
under targeted correct remediation but not under misaligned or generic feedback?

## 2. Hypotheses (preregistered)

- **H1 可训性**: SFT on malrule-grounded multi-turn dialogues yields turn-probe
  consistency above the prompt-only baseline of the *same* base model, at every
  size ≥1.7B. (0.6B allowed to fail; it is the floor anchor.)
  **Test**: per size, hold-consistency (trained, best data scale) minus baseline,
  3-seed mean with 95% t-CI excluding 0; per-seed points reported.
- **H2 规模律**: holding stability increases monotonically-ish with model size and
  with training-data scale (1k → 4k → 16k dialogues); we report curves with 95% CIs
  over 3 seeds, not point claims.
- **H3 选择性翻转 (headline control)**: trained simulators flip beliefs under
  *targeted correct* remediation at a higher rate than under *misaligned*
  (wrong-misconception) or *generic* ("try again") feedback.
  **Test**: selectivity = targeted-flip − max(misaligned-flip, generic-flip);
  selectivity(trained) − selectivity(prompt-only baseline) > 0 with 95% t-CI
  over 3 seeds excluding 0.
  **Failure condition**: if flip-selectivity ≤ prompt-only baseline, the headline
  claim fails and is reported as such — stubbornness alone is an artifact, not success.
- **H4 双语**: the 中文 arm reproduces the qualitative pattern of H1–H3
  (direction, not magnitude).
- **H5 附带损伤控制**: on non-malrule (correct-solving) probes under the
  correct-student persona, trained simulators stay within **5 percentage points
  (absolute, 3-seed mean, per size)** of the same-size base model's accuracy.
  Motivated by arXiv:2604.00818's finding that single-misconception training
  over-applies unless correct examples enforce boundaries.

## 3. Metrics (all code-computed; zero LLM judges in headline numbers)

1. **Turn-probe consistency**: at each dialogue turn t, inject a probe problem;
   the assigned malrule's `malrule_algorithm.py` computes the expected wrong answer;
   the simulator's final answer is extracted by the frozen deterministic extractor
   `harness/answer_eq.py::extract_final_answer` and matched via the frozen
   comparator `answers_equal` (string normalization → numeric equivalence incl.
   fractions/percent/float-tail, rel/abs tol 1e-9 → symbolic whitespace/case-
   insensitive fallback; no CAS). Pilot smoke motivated this: naive exact match
   misjudges "0/6" vs "0" and float tails like "251.99999999999997".
   Protocol details (on-policy student turns, scripted tutor turns, discarded
   probe forks, k=0 anchor): DECISIONS D-012, `harness/probe_eval.py`.
   Report consistency-vs-turn (drift) curves.
2. **Selective Flip Score (multi-turn)**: post-remediation probe correctness under
   {targeted, misaligned, generic} feedback conditions; selectivity = targeted-flip
   rate minus max(misaligned, generic) flip rate.
3. **Collateral damage**: accuracy on held-out correct-solving probes
   (`correct_algorithm.py` ground truth) vs. base model.
4. Auxiliary (non-headline, labeled as such): persona-plausibility spot checks may
   use human eyes only, never an LLM judge.

## 4. Experimental grid

- Sizes: Qwen3 {0.6B, 1.7B, 4B, 8B, 14B}, original hybrid series,
  `enable_thinking=False`, as-served decoding discipline (temperature 0.7,
  top_p 0.8, top_k 20; eval decoding seed 7 for all cells and baselines, D-014).
- Seeds: 3 per cell (14B: reduced to anchor runs as budget requires — record which).
- Data scale: {1k, 4k, 16k} dialogues (EN). 中文 arm at one scale (4k) ×
  {1.7B, 4B, 8B} per D-015.
- Method arms: SFT (all cells; per-size recipe frozen in D-014); DPO on top of
  SFT at 4B/8B (pairs: hold-consistent vs. leak/collapse continuations; exact
  pair-construction protocol to be fixed by dated amendment BEFORE any DPO run).
- Baselines: prompt-only base models (same probes, same harness). Optionally,
  a larger open-weight instruct model prompt-only for context, only if staging
  to the offline cluster permits — absence is not a deviation.
- ≈54 runs total; est. 1,000–1,500 A100-hours, whole-node (8×A100-80G) jobs,
  FSDP/DDP; LoRA fallback documented as amendment if full-param infeasible at 8B/14B.

## 5. Data pipeline (answer-leak-proof by construction)

- Problems & math: MalruleLib `problem_generator.py` + executable malrule/correct
  algorithms (pinned commit `8ddedfb`). **Student mathematical content is computed by
  code**, including step traces (2604.00818: step traces are essential).
- Natural-language surface: GLM-5.3 via the institutional gateway drafts *tutor* turns and student
  *phrasing around* the code-computed math. GLM never invents student math.
- Mix-in: no-malrule correct-solving dialogues (boundary enforcement per 2604.00818).
- Audits before scale-up: hand-audit ≥200 pilot dialogues for (a) tutor answer-leak
  before remediation point, (b) surface-vs-computed-math contradiction. Preregistered
  bar: leak rate <2% after prompt iteration, else pipeline redesign before main runs.
- Probe sets: frozen with SHA-256 in `docs/DECISIONS.md` (probes_hold_en 1992,
  probes_correct_en 1000); never trained on.
- Eval dialogues: held-out scaffold set (seed 20267777, 327 scaffolds → 318
  rendered; the rendered set is the frozen eval set), problem texts disjoint
  from probes and from the 16k training pool (D-012); never trained on.
- Data-scale subsets are nested 1k ⊂ 4k ⊂ 16k (D-013). A grid cell trains on
  the successfully-rendered dialogues within its scaffold subset; render yield
  is reported per scale (4k: 3865/4001 = 96.6%).

## 6. Timeline (Aug 25–31)

- **8/25**: scope freeze; day-0 gates (done, PASS); repo scaffold; Qwen3 weights
  download (~57GB, ModelScope); pilot 200 dialogues + leak audit.
- **8/26**: dev machine recreation; rsync staging; smoke SFT (0.6B, 200 dialogues);
  freeze EN probe sets + **preregistration freeze commit**; launch first grid cells.
- **8/27**: full grid launch gate. If grid cannot launch by EOD → fall back to TiJian
  (preregistered fallback, shares staged Qwen3 weights).
- **8/28–8/30**: grid runs; 中文 arm; DPO arm; drift/flip analysis as cells land.
- **8/31**: 14B anchors done; CI aggregation; writeup skeleton; release prep.
- September evenings: writeup polish, release (GitHub+Gitee, ModelScope mirror).

## 7. Stop / failure conditions (preregistered)

- Pilot leak rate ≥2% after two prompt iterations → redesign before any main run.
- Grid not launched by 8/27 EOD → TiJian fallback.
- H3 failure is a *reportable negative result*, not a reason to iterate the metric.
- No "first/SOTA/solved" claims anywhere; deltas stated against the Sonkar-group
  line of work explicitly (see DECISIONS D-004).

## Amendments

### A-1 (2026-08-26): DPO pair-construction protocol (fixes PLAN §4, committed BEFORE any DPO run)

- **Scope**: secondary arm; sizes {4B, 8B}, EN, 4k scale only; seeds {17, 1017,
  2017}; cells `en-dpo-{SIZE}-4k-s{SEED}`. No headline change; H3 remains the
  SFT-arm claim.
- **Source contexts**: the frozen 4k EN rendered training dialogues only (the
  exact set the 4k SFT cells trained on). No new problems; probes and eval
  dialogues untouched.
- **Pair sites** (deterministic walk, sorted by (dialogue_id, turn index)):
  - *hold-sites*: student turns of kind {solve_malrule, reaffirm_malrule,
    hold_after_misaligned} — desired behavior is malrule-consistent (≤2 per
    dialogue, first-come).
  - *flip-sites*: student turns of kind {flip_redo} — desired behavior is the
    correct answer after targeted remediation (≤1 per dialogue).
  - Sites where correct_answer == malrule_answer, or where the correct answer
    appears verbatim in the problem text, are skipped (same exemption logic as
    the renderer leak checks).
- **Chosen** = the rendered turn text (already hard-check-verified).
- **Rejected** = counterfactual continuation generated by GLM via the institutional gateway
  (generation-side use only; zero-LLM-judge holds — acceptance is code-checked):
  - at hold-sites: a premature-capitulation turn (student abandons their method
    without targeted remediation). Accept iff contains_token(correct_answer)
    and NOT contains_token(malrule_answer).
  - at flip-sites: a stubborn-persistence turn (student re-asserts the malrule
    answer despite targeted remediation). Accept iff contains_token(
    malrule_answer) and NOT contains_token(correct_answer).
  - ≤3 attempts per site, then the site is dropped; drop counts reported.
- **Balance** (selectivity-preserving core): equal counts of hold-preference
  and flip-preference pairs overall — downsample the majority class with rng
  seed "dpo-pairs-v1"; final counts recorded in the decision log.
- **Format**: same chat template as train_sft; input = student system prompt
  (with misconception) + dialogue history up to the site; chosen/rejected are
  the two candidate student turns.
- **Recipe (frozen)**: standard DPO, β = 0.1, init from the same-size 4k SFT
  cell checkpoint of the SAME seed; lr 5e-7, 1 epoch, global batch 32, other
  hyperparameters as the SFT recipe (D-014).
- **Readout (preregistered)**: paired-by-seed diffs DPO vs the same-size 4k
  SFT cells on the frozen harness — hold rate, trained selective-flip, and the
  correct-persona guardrail (5pp tolerance vs the SFT cell), 3-seed t-CI
  (df=2) as elsewhere. Either direction is reportable; no metric iteration.
