# HoldFast 执迷 — writeup skeleton (v1, 2026-08-27)

> Status: ALL planned experiments complete and all `[TBD]`s filled — full EN
> grid (12 rows), zh arm, DPO arm (4B+8B), 14B-4k anchors (full 3 seeds),
> all with the frozen prereg harness. Numbers final unless a new prereg
> amendment reopens something.
> Writing discipline (preregistered): no "first/SOTA/solved" claims; deltas
> stated against the Sonkar-group line of work explicitly (D-004).

## Title (working)

HoldFast: training small open models to hold assigned math misconceptions
through multi-turn tutoring — and to yield only to targeted remediation.

## Abstract (stub)

Student simulators for tutor training must *stay wrong on purpose*: keep an
assigned misconception under generic pressure, yet flip when the tutor
actually addresses the error. We SFT Qwen3 models (0.6B–14B) on
GLM-rendered dialogues whose every turn is hard-checked against code-computed
math from MalruleLib malrules, and evaluate with code-only probes (zero LLM
judges in headline metrics). Trained 8B holds its assigned misconception on
.82 of dialogue probes (prompt-only base: .13) while flipping on targeted
remediation at .78 vs .00 on misaligned remediation; prompt-only baselines
flip indiscriminately (.65 vs .59). Selectivity is trained, not prompted,
and the gap persists at 14B against the strongest prompt-only base
(hold .80 vs .31, selectivity +0.62 over base).
Preregistered analysis, 3 seeds/cell, 95% t-CIs; bilingual EN/zh arm; full
open release (data, code, adapters/checkpoints per license).

## 1. Motivation

- Tutor-training / teacher-education tools need believable struggling
  students; believability = *consistent* misconception enactment, not random
  errors.
- Prompt-only LLM students collapse to the correct answer under generic
  "are you sure?" pressure (our baselines: hold .01–.13) — the well-documented
  sycophancy/capitulation failure mode.
- The desired behavior is a *selective* policy: hold under generic and
  off-target pressure, flip under remediation that names the specific error.
  This is H3, the headline claim.

## 2. Relation to prior work (explicit deltas, D-004)

- Sonkar et al. line (MalAlgoPy / student simulation; incl. Chen, Liu, Sonkar,
  arXiv:2601.03217 — MalruleLib): defined malrule-based student modeling,
  single-turn settings, SFT+DPO on 4B/8B, English.
- Our deltas: (a) multi-turn *persistence under pressure* as the target
  behavior and metric; (b) selective-flip control as the headline test;
  (c) code-computed turn-by-turn probes, zero LLM judges in headline metrics;
  (d) scaling curves 0.6B–8B × {1k,4k,16k} × 3 seeds plus a full-3-seed
  14B-4k anchor row, all with preregistered CIs; (e) bilingual EN/zh arm;
  (f) preregistration frozen
  before the main grid (PLAN.md v1.0, commit 8c1fe4b).
- MalruleLib attribution & license red lines: share-alike; no evaluation of
  commercial closed models; credit Chen/Liu/Sonkar throughout.

## 3. Method

### 3.1 Task & data pipeline (leak-proof by construction)
- Malrules: 102 misconception rules with executable probes (MalruleLib).
- Scaffolds: code-generated turn plans + pre-computed math (problems, malrule
  steps/answers, correct steps/answers); dialogue types: hold, flip_targeted,
  flip_misaligned, control_correct.
- Rendering: GLM (institutional gateway) writes *prose only*; every turn is
  hard-checked (answer containment, leak bans: correct answer may not appear
  before remediation); 3 attempts then drop. Yields: EN main 3865/4001 at 4k,
  15298/15849 at 16k (96.5%), zh main 3867/4001, eval EN 318/327, zh 319/327.
- Nested data scales 1k ⊂ 4k ⊂ 16k (D-013).

### 3.2 Evaluation (frozen harness)
- Dialogue-mode probes: mid-dialogue answer probes at fixed ks; static-mode
  persona probes (misconception persona, correct persona).
- Extraction: strong-cue "Answer:" path + last-numeric fallback; frozen.
- Metrics: hold consistency; targeted/misaligned/generic flip rates;
  selective flip = targeted − misaligned; static enactment; correct-persona
  accuracy (H5 guardrail). All code-computed; zero LLM judges.
- Prereg tests: 3-seed mean diff vs same-size prompt-only baseline, 95% t-CI
  (df=2, t=4.303) excluding 0 (H1/H3); H5 tolerance 5pp.

### 3.3 Training
- SFT: per-size recipe frozen (D-014); student-side loss masking only.
- DPO arm (A-1): pairs = rendered hold/flip turns (chosen) vs GLM
  counterfactuals (rejected: premature capitulation at hold sites, stubborn
  persistence at flip sites), code-checked; balanced classes; β=.1, lr 5e-7,
  init from same-seed SFT cell. Results in §4.6 (null at 4B,
  null-to-marginal at 8B).

## 4. Results

### 4.1 H1 — trained holding (PASS, 12/12 rows)
- Hold consistency, trained vs base: strongest cell 8B-16k .823 vs .132,
  diff +0.691 [+0.672,+0.711]; 8B-4k +0.646 [+0.632,+0.661]; all 12 rows'
  CIs exclude 0. Fig: hold_scaling.
- 14B anchor (4k, 3 seeds): hold .805/.795/.791 vs base .309 — H1 diff
  +0.488 [+0.471,+0.505], PASS. The 14B base is by far the strongest
  prompt-only model (next: 8B base .132), and the trained gap still
  clears it by ~.49.

### 4.2 H2 — scaling (monotone on the full grid)
- Hold rises with model size at every scale and with data at every size, on
  all 12 rows (Figs: hold_scaling, hold_data_scaling). 8B: .66 (1k) → .78
  (4k) → .82 (16k).
- Prereg deliverable for H2 is the curves themselves with 95% CIs ("not
  point claims") — Figs hold_scaling + hold_data_scaling satisfy it.
  The 14B-4k anchor extends the size-monotone hold at 4k:
  .42 → .46 → .69 → .78 → .80 (0.6B→14B).
- Notable at 8B-16k: H5 diff is *positive* (+0.062 — correct-persona
  accuracy improves over base), misaligned flip .000, other frac .17.

### 4.3 H3 — selective flip (headline; PASS 12/12 rows)
- Money plot (selectivity_4k): trained targeted flip .45→.74 with size,
  misaligned/generic ≤.02 at 4B/8B; base models flip near-indiscriminately
  (8B base: targeted .65, misaligned .59).
- Trained selective-flip diff vs base: 8B-16k +0.729 [+0.718,+0.741]
  (trained selectivity .78, misaligned flip .000); 8B-4k +0.669
  [+0.628,+0.710]; 14B-4k +0.622 [+0.585,+0.658] against the
  least-indiscriminate base (base selectivity +0.157).
- Timeline view (drift_8B_4k, panel b): trained P(malrule) rides .75–.85
  through k=0–2, crashes to ≤.04 exactly at the k=3 remediation turn under
  *targeted* remediation, and stays flat ~.75 under *misaligned* remediation
  — the flip tracks the remediation event, not dialogue length. Panel (a):
  hold probes stay flat .77–.81 across k=0–5 while base decays .21→.11.

### 4.4 H4 — bilingual arm (PASS with a guardrail qualification)
- zh data: same scaffolds, GLM-translated problem texts (verbatim-math
  verified mechanically + 100-probe hand audit), language-neutral probe
  subset (hold 1759/1992, correct 879/1000). D-019.
- zh prompt-only baselines replicate the EN failure mode: hold .026/.131/.211
  (1.7B/4B/8B), misaligned+generic flip .50–.67 (near-indiscriminate
  capitulation); base selectivity ≤ +0.18.
- Trained zh (4k, 3 seeds): H1 and H3 PASS at all three sizes — zh-8B holds
  .774 vs base .211 (H1 +0.563 [+0.549,+0.577]) and flips targeted .74 vs
  misaligned .04 (H3 +0.524 [+0.483,+0.564]). Hold runs only slightly below
  EN at matched size (.43/.67/.77 vs .46/.69/.78); 'other' fractions match
  EN to ±.01, i.e. the language-neutral subset held the instrument constant.
  Fig: figs_zh/selectivity_4k.
- Qualification: **the H5 guardrail is systematically tighter in zh** —
  all sizes negative and larger in magnitude than EN counterparts; 1.7B
  (−6.3pp) and 8B (−5.7pp) breach the 5pp tolerance, 4B (−3.9pp) is within.
  (EN breaches only at 0.6B.) Holding transfers cross-lingually; the
  correct-persona cost is higher in zh. Reported as-is per prereg §7.

### 4.5 H5 — correct-persona guardrail
- 4B/8B within tolerance (8B-4k +0.004). **0.6B breaches at 4k (−9.6pp) and
  16k (−6.2pp)** — preregistered breach, reported as-is: the smallest model
  pays for holding with degraded correct-persona math. Fig: guardrail_h5.

### 4.6 DPO arm (A-1): null at 4B, null-to-marginal at 8B

- Setup: 2134 balanced pairs from the frozen 4k EN dialogues (chosen =
  rendered hold/flip turn; rejected = code-checked GLM counterfactual:
  premature capitulation at hold sites, stubborn persistence at flip sites);
  policy AND reference init from the same-seed 4k SFT cell; β=.1, lr 5e-7,
  1 epoch (66-67 steps).
- 4B-4k, paired by seed (3 seeds): every headline metric's paired diff CI
  includes 0 — hold +0.001 [−0.054,+0.056], targeted +0.027 [−0.041,+0.096],
  selectivity +0.026 [−0.031,+0.084]; the only CI excluding 0 is H5 accuracy
  +0.005 [+0.003,+0.007]. Direction mildly positive, magnitude nil:
  **with this pair recipe, DPO on top of SFT adds nothing detectable at 4B.**
  Reported as-is per amendment A-1.
- 8B-4k (retrained under the hardened save, D-025; paired by seed): the
  arm stays null-to-marginal — the only paired CI excluding 0 is a +2.2pp
  targeted-flip gain (+0.022 [+0.008,+0.036]); hold −0.013 [−0.038,+0.012],
  selectivity +0.014 [−0.002,+0.031], H5 −0.004 [−0.027,+0.018] all include
  0. **With this pair recipe, DPO on top of SFT adds at most a marginal
  targeted-flip improvement at 8B and nothing detectable elsewhere.**
- Reading: the SFT cells already sit near the behavior the pairs encode
  (misaligned flip ≤.04 before DPO); the preference margin trains (rewards/
  accuracies →.9 within 10 steps) but the policy barely moves at lr 5e-7
  (drift gate: max weight change vs init 3e-5 at 8B).
- Engineering note (D-021): TRL's precompute_ref_log_probs runs before
  accelerate places the model under FSDP; fix = pre-place the bf16 model on
  the local rank before handing it to the trainer (device-placement only).
  (D-025): FSDP checkpoint saves need both a synchronized/verified gather
  AND a semantic gate — for DPO, a drift bound vs the init (lr 5e-7 keeps
  healthy drift ~1e-3; save-time corruption showed up at 2.6–17.6).

### 4.7 14B anchors (full 3 seeds, 4k)

- Contrary to the prereg's "may be reduced seeds" allowance, the 14B-4k
  anchor ran the full 3 seeds: hold .805/.795/.791, targeted flip
  .780–.797, misaligned flip .000–.017, selectivity .780/.793/.764,
  H5 acc .675/.688/.693 (base .665 → H5 diff +0.020, within tolerance).
- Tests: H1 +0.488 [+0.471,+0.505] PASS; H3 +0.622 [+0.585,+0.658] PASS
  (base selectivity +0.157, the highest of any base). 'other' fraction .20,
  in line with 8B (.21).
- The interesting control: the 14B *base* is qualitatively better than
  smaller bases (hold .309 vs 8B's .132, selectivity +0.157) — prompt-only
  misconception enactment does improve with scale — but it still flips
  indiscriminately (misaligned .400, generic .409). Training closes that
  gap: misaligned flip drops to ≈.01 while targeted stays .78.
- Engineering: 14B trains on 4×A100-80G under FSDP with
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True and a DCP-based
  verified save; ~85 min/cell end-to-end (D-022/D-024).

## 5. Measurement audit (transparency)

- 'other' bucket audit: at 8B, ~41% of 'other' dialogue-probe responses
  contain the malrule answer in the tail (extraction artifacts: expression/
  ratio/united answers truncated to numeric fragments), ~8% the correct
  answer; residual true-other ≈11% of probes. Artifact share grows with
  model size ⇒ reported hold rates *understate* large-model holding; both
  arms measured with the same frozen instrument ⇒ H1/H3 diffs conservative.
- Per-malrule view (Appendix D) localizes the artifacts: of the 12 malrules
  with hold < .50 at 8B-4k, 10 have 'correct' ≈ 0 and 'other' .60–1.00
  (pooled: correct .055, other .791, n=345) — unparseable answer forms, not
  capitulation. Genuine capitulation is confined to 2 malrules; excluding
  artifact rows, per-malrule hold at 8B has median .97.
- Dialogue-mode probe pools: deterministic skips where pool < n_student+1
  (D-018); zh pools are subsets (D-019).

## 6. Limitations

- Extractor truncation (above) — frozen per prereg; a richer matcher is
  future work, changes would require a new prereg.
- 0.6B H5 breach: holding hurts correct-persona math at the smallest scale.
- Misconception coverage: 102 malrules, middle-school arithmetic/algebra
  focus; probe answers restricted to language-neutral forms in zh.
- Rendered tutor text is GLM-authored; style monoculture possible.
- 14B on 4×A100-80G is feasible but tight: requires expandable_segments
  and a DCP-based verified save (D-022/D-024); the summon-based live-gen
  canary OOMs at 14B and is skipped (post-save, non-fatal). Scales beyond
  14B were out of scope for this node shape.

## 7. Release

- Code + scaffolds + rendered dialogues + probes + analysis + figures;
  checkpoints/adapters per base-model licenses; MalruleLib share-alike
  honored; no commercial closed-model evaluations anywhere.
- Preregistration: PLAN.md v1.0 (8c1fe4b) + dated amendments (A-1) +
  decision log D-001..D-019.

## Appendices (planned)

- A: full grid tables with CIs (from results_interim docs).
- B: prompt texts — docs/appendix_b_prompts.md (AST-extracted from
  harness sources; code is source of truth).
- C: audit protocols + samples (zh 100-probe, 'other' 30-sample).
- D: per-malrule breakdowns — docs/appendix_d_8B_4k.md (with artifact-
  localization reading) + docs/appendix_d_0.6B_4k.md +
  docs/appendix_d_14B_4k.md + docs/appendix_d_zh_8B_4k.md +
  docs/appendix_d_dpo_8B_4k.md; script
  harness/per_malrule.py (descriptive, 3 seeds pooled). 14B replicates the
  8B artifact pattern (median per-malrule hold .97; the 10 low-hold
  malrules have other@hold ≈ .6–1.0, i.e. unparseable answer forms).
