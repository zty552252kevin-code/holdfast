# HoldFast: Training Small Open Models to Hold Assigned Math Misconceptions Through Multi-Turn Tutoring — and to Yield Only to Targeted Remediation

**Kevin Zhao**
*Draft v1.0 (2026-08-27). Code, data, and checkpoints: see §9 (Release).*

## Abstract

Student simulators for tutor training must *stay wrong on purpose*: keep an
assigned misconception under generic pressure, yet flip when the tutor
actually addresses the error. We SFT Qwen3 models (0.6B–14B) on GLM-rendered
tutoring dialogues whose every student turn is hard-checked against
code-computed math from MalruleLib misconception rules ("malrules"), and we
evaluate with code-only turn-by-turn probes — zero LLM judges in any headline
metric. A trained 8B model holds its assigned misconception on .82 of
dialogue probes (same-size prompt-only baseline: .13) while flipping under
targeted remediation at .79 versus .01 under misaligned remediation;
prompt-only baselines flip near-indiscriminately (targeted .65 vs misaligned
.59). Selectivity, in this setup, is trained rather than prompted, and the
gap persists at 14B against the strongest prompt-only baseline (hold .80 vs
.31; selectivity difference +0.62). The full study is preregistered (frozen
before any main-grid run) with 3 seeds per cell and 95% t-confidence
intervals: a 13-row size × data grid, a Chinese-language arm, a DPO arm
(a null-to-marginal result, reported as preregistered), and preregistered
guardrail breaches at 0.6B and in the Chinese arm, reported as-is. We
release code, generators, dialogues, frozen probe sets, and exemplar
checkpoints, under the licenses detailed in §9.

## 1. Introduction

Tutor-training and teacher-education tools need believable struggling
students. Believability here is not random error injection: a student who
holds the misconception "you cannot subtract a bigger number from a smaller
one" makes *systematic* errors, keeps making them under ordinary follow-up
questioning, and — crucially — can be talked out of them by instruction that
actually names and addresses the error.

Prompt-only LLM students fail this on both ends. Under generic pressure
("are you sure?"), they collapse to the correct answer: across our five base
models, prompt-only hold consistency is .01–.31 (§6.1), the well-documented
sycophancy/capitulation failure mode. And when they do flip, they flip
indiscriminately: our 8B base flips at .65 under targeted remediation but
also at .59 under remediation aimed at a *different* misconception (§6.3).
Neither behavior makes a useful practice partner for a novice tutor.

The behavior we want is a *selective policy*:

- **hold** the assigned misconception under generic pressure and under
  off-target remediation, but
- **flip** when remediation names and corrects the specific error.

A simulator that never yields is a stubbornness artifact, not a student; we
preregistered this as an explicit failure condition (a trained model whose
flip-selectivity does not exceed the prompt-only baseline fails the headline
hypothesis, however well it holds).

**What we do.** We build a data pipeline in which all student mathematics —
wrong answers, wrong step traces, and correct-solving counterparts — is
computed by executable misconception rules from MalruleLib (Chen, Liu &
Sonkar, 2026), and an LLM (GLM-5.3) writes *prose only*, hard-checked
turn-by-turn against the code-computed math. We SFT Qwen3 models at five
sizes (0.6B–14B) on these dialogues and evaluate with a frozen, code-only
probe harness that injects probe problems at every turn of held-out
dialogues; every headline number in this paper is computed by deterministic
extraction and comparison code, never by an LLM judge.

**What we find** (all tests preregistered; PLAN frozen at commit `8c1fe4b`
before any main-grid run):

1. **Trained holding (H1).** SFT lifts multi-turn hold consistency far above
   the same-size prompt-only baseline at every grid cell — 13/13 rows PASS
   with 95% t-CIs excluding 0 (e.g. 8B-16k: .82 vs .13).
2. **Scaling (H2).** Hold consistency rises monotonically with model size at
   every data scale and with data scale at every size, on all rows.
3. **Selective flipping (H3, headline).** Trained models flip under targeted
   remediation (.45–.79 across sizes at the 4k scale) while flipping under
   misaligned or generic feedback at ≤.04 from 4B up; base models flip
   near-indiscriminately. The selectivity difference over baseline passes at
   all 13 rows. Turn-resolved curves show the flip is *event-locked*: P(malrule
   answer) crashes exactly at the remediation turn under targeted remediation
   and stays flat under misaligned remediation (§6.3).
4. **Bilingual transfer (H4).** The pattern replicates in Chinese at all
   three sizes tested, with one qualification: the correct-persona guardrail
   (H5) is systematically tighter in Chinese, breaching tolerance at 1.7B and
   8B (§6.4).
5. **Collateral damage (H5).** From 1.7B up (EN), holding costs little or no
   correct-persona accuracy (8B-16k actually improves on it, +6.2pp). The
   0.6B model breaches the preregistered 5pp tolerance at 4k and 16k — a
   preregistered negative result, reported as-is.
6. **DPO adds little on top of SFT (preregistered secondary arm).** With
   our pair recipe, paired-by-seed DPO-vs-SFT differences are null at 4B and
   null-to-marginal at 8B (only targeted flip excludes 0, +2.2pp).

**Positioning.** The single-turn version of this problem, and the
misconception library we build on, come from the Sonkar group (§2). Our
contribution is not the concept of malrule-based student simulation, but:
full multi-turn persistence as the trained behavior and the measured
quantity; multi-turn selective flipping under {targeted, misaligned,
generic} feedback as the headline control; a code-only turn-by-turn probe
harness; a preregistered size × data × seed grid with confidence intervals;
a bilingual arm; and an open release of code, data, probes, and exemplar
checkpoints.

## 2. Relation to prior work

Our study sits directly on a line of work by the Sonkar group; we state the
deltas explicitly.

- **MalruleLib** (Chen, Liu & Sonkar, arXiv:2601.03217; ACL Main 2026)
  provides 102 executable misconception rules ("malrules") across 22
  categories of middle-school arithmetic and algebra, each with a problem
  generator, a malrule algorithm producing the misconception-consistent
  wrong answer and step trace, and a correct algorithm. It is the source of
  all mathematics in this paper (pinned commit `8ddedfb`; 2 of 102 malrules
  excluded for broken automated test suites). MalruleLib is distributed
  under a custom non-commercial share-alike license whose terms explicitly
  permit training open-weight models; we honor it throughout
  (§9), and per its terms we do not evaluate any commercial or closed-source
  model anywhere in this project.
- **Misconception acquisition dynamics** (arXiv:2604.00818, same group)
  trains single-misconception student models in a *static* problem-solving
  setting (no dialogue), English only. We import two design lessons with
  attribution: training data must include intermediate step traces, and it
  must mix in correct-solving examples to enforce misconception boundaries
  (this motivates our H5 guardrail).
- **Selective Flip Score** (arXiv:2605.12748, same group) names the
  sycophancy-vs-simulation tension and defines selective flipping in a
  primarily *single-turn* setting (with one exploratory multi-turn variant),
  at Qwen3-4B / Llama3.1-8B scale, English only, with no code, data, or
  weights released at the time of writing.

**Our deltas**: (a) full multi-turn tutoring dialogues with turn-by-turn
executable probes and drift curves, rather than single-turn scoring;
(b) multi-turn selective flipping under three feedback conditions
{targeted, misaligned, generic} as the headline, preregistered test;
(c) zero LLM judges in headline metrics — extraction and comparison are
frozen deterministic code; (d) a 0.6B–14B × {1k, 4k, 16k} × 3-seed grid
with 95% CIs, preregistered before the first main run; (e) a bilingual
EN/zh arm; (f) an open release of code, generators, dialogues, probes,
and exemplar checkpoints (§9).

We make no priority claims beyond these deltas. The sycophancy failure mode
of assistant-tuned LLMs is well documented in the alignment literature and
is treated here as background.

## 3. Task and data

### 3.1 Task

A single student-simulator model serves all misconceptions: the assigned
malrule is carried in the system prompt (its natural-language description
from MalruleLib), and correct-solving dialogues use a correct-student
persona instead. This matches deployment (a tutor-trainer assigns a persona
at runtime) and makes selectivity meaningful — the model must *read* the
assigned misconception, not memorize one.

Training dialogues come in four scripted types, all built on code-computed
math:

- **hold**: the tutor presses with generic challenges ("are you sure?
  walk me through it"); the faithful student re-derives the malrule answer.
- **flip_targeted**: at a fixed remediation turn, the tutor names the
  specific error and demonstrates the correct method; the faithful student
  flips and re-solves correctly.
- **flip_misaligned**: the remediation addresses a *different* misconception;
  the faithful student holds.
- **control_correct**: no malrule; a correct-persona student solves
  correctly (the boundary-enforcement mix-in).

### 3.2 Pipeline: code computes the math, the LLM writes prose

For each dialogue, a scaffold generator draws a problem from the malrule's
MalruleLib generator and precomputes everything mathematical: the malrule
answer and step trace, the correct answer and steps, and the turn plan.
GLM-5.3 (via an institutional gateway) then renders the scaffold into
natural dialogue — but every rendered turn is hard-checked against the
scaffold: the student's final answer must contain the code-computed malrule
(or, post-remediation, correct) answer; the tutor must not leak the correct
answer before the remediation turn (with an exemption where the correct
answer literally appears in the problem statement); problem statements must
appear verbatim; remediation must contain the correct answer. A render
gets ≤3 attempts, then the dialogue is dropped. Yields: 15,298/15,849 EN
dialogues rendered (96.5%); the nested subsets contain 3,923/4,001 rendered
dialogues at the 4k scale and 980/1,000 at 1k; eval set 318/327. Per-cell
training logs record exactly what each cell trained on: all 4k and 16k
cells match these counts, while the 1k cells — launched while the final
render batch was still syncing — trained on 977 of the 980 (the 3,865
figure at 4k frozen in the preregistration was a mid-render snapshot;
both clarifications recorded in D-027).

The renderer never invents student math, so answer leakage is a property to
*audit* on the tutor side rather than *hope for* on the student side, and
turn probes are exact-match verifiable by construction. Before any main
run, an automated leak scan over all 198 rendered pilot dialogues found
zero pre-remediation answer leaks (preregistered gate: <2%), alongside an
archived 30-dialogue hand-review sample; the preregistration's wording
called for a ≥200-dialogue *hand* audit, so we record the executed check
as a deviation (D-027).

Data scales are nested (1k ⊂ 4k ⊂ 16k) by deterministic per-type subsetting,
which removes subset-resampling variance from the data-scale axis.

### 3.3 Chinese arm

MalruleLib generates English problem text only, so the zh arm translates
surface text while keeping all math verbatim: GLM translates the 12,701
unique strings (problem texts, misconception descriptions) at temperature 0
under a per-item hard check — the numeric-token multiset and single-letter
variables must survive translation verbatim (100% coverage after
single-item rescues). A 100-probe audit — performed by the operator's
coding agent with mechanical token checks, sample archived for human
re-review (D-019) — found 100/100 verbatim-math
(preregistered bar ≥98%). zh probe sets are the frozen EN sets restricted
to language-neutral answers (no ASCII alphabetic runs ≥2 in either the
correct or the malrule answer): 1759/1992 hold probes, 879/1000 correct
probes. The same 4k scaffolds are rendered in Chinese under the same hard
checks (3867/4001; eval 319/327). The probe template keeps the literal
"Answer:" marker so the frozen extractor applies unchanged across arms.

## 4. Evaluation: code-only turn-by-turn probes

### 4.1 Probe protocol

**Dialogue mode** (H1/H2/H3). Evaluation dialogues are held out (problem
texts disjoint from both probe sets and the entire 16k training pool by
construction). The system prompt assigns the misconception; tutor turns are
*scripted* from the rendered eval dialogue; student turns are generated
**on-policy** by the model under evaluation. At k=0 (pre-dialogue anchor)
and after each on-policy student turn, we fork the conversation with a probe
problem of the same malrule ("Try this one: ..."), record the model's
answer, and discard the fork — probes never contaminate the main
trajectory. Probe problems are drawn deterministically per dialogue from
the frozen probe sets.

**Static mode.** Single-turn probes under a persona: misconception-persona
on hold probes (enactment) and correct-persona on held-out correct-solving
probes (the H5 collateral-damage guardrail).

**Classification is frozen code.** A deterministic extractor pulls the
final answer (strong-cue "Answer:" path with a last-numeric-candidate
fallback), and a frozen comparator (string normalization → numeric
equivalence including fractions/percents/float tails → symbolic fallback;
no CAS) classifies each response as {malrule, correct, other}. The 'other'
fraction is reported and hand-audited (§6.6). No LLM judges anywhere in
headline metrics; the only LLM-generated artifacts in evaluation are the
frozen eval-dialogue *scripts* themselves, produced and frozen before the
models they evaluate were trained.

**Metrics.** Hold consistency = P(malrule answer | hold dialogues, k≥1).
Targeted flip = P(correct | flip_targeted, k≥3, i.e. post-remediation);
misaligned flip likewise on flip_misaligned dialogues; generic flip =
P(correct | hold dialogues, k≥4, post generic-challenge). Selectivity =
targeted flip − max(misaligned flip, generic flip). Per-cell bucket sizes
are constant across all cells and baselines within each arm (EN: hold 660,
targeted 182, misaligned 120, generic 264 probe records; static 1820/1000.
zh: 625/170/114/250; static 1629/879).

**Decoding** follows the as-served Qwen3 non-thinking discipline
(temperature 0.7, top_p 0.8, top_k 20), eval seed fixed at 7 for every cell
and baseline. Baselines (prompt-only base models) use the same system
prompts, probes, and harness.

### 4.2 Preregistration and statistics

The full plan — hypotheses, tests, tolerances, grid, recipes, and failure
conditions — was frozen (commit `8c1fe4b`) before any main-grid run;
post-freeze changes are dated amendments (the only one: A-1, the DPO pair
protocol, committed before any DPO run). Probe sets are frozen with
SHA-256 digests.

Each grid row = 3 training seeds {17, 1017, 2017}. Tests are 3-seed mean
differences vs the same-size prompt-only baseline with 95% t-CIs (df=2,
t=4.303): **H1** hold-consistency difference excludes 0; **H3** selectivity
difference excludes 0 (failure condition: a trained model whose selectivity
does not exceed baseline fails the headline claim); **H5** correct-persona
accuracy not more than 5pp (absolute) below the same-size base —
operationalized one-sided as a collateral-damage bound (breach iff the
diff < −0.05; improvements are not breaches). **H2** is reported as
curves with CIs, not a point test. **H4** claims direction, not magnitude,
in the zh arm. Breaches are reported as-is; the metric is never iterated
post-hoc.

## 5. Training

**SFT** (all cells): loss on student (assistant) tokens only, via
incremental-prefix tokenization; 2 epochs, global batch 32 (WORLD_SIZE-aware
gradient accumulation), cosine schedule, 3% warmup, max length 2048, bf16.
Per size: 0.6B/1.7B micro-batch 4, lr 2e-5, DDP; 4B micro-batch 2, lr 2e-5,
DDP; 8B micro-batch 2, lr 1e-5, FSDP full-shard + gradient checkpointing;
14B micro-batch 1, lr 1e-5, FSDP full-shard + gradient checkpointing (14B
additionally requires the PyTorch expandable-segments allocator on
4×A100-80G). Qwen3 hybrid models run with thinking disabled throughout.

**DPO** (amendment A-1; 4B/8B, EN-4k, 3 seeds). Pairs come from the frozen
4k training dialogues only: at *hold sites* (student turns whose faithful
behavior is malrule-consistent), chosen = the rendered turn, rejected = a
GLM-generated premature capitulation (accepted only if it contains the
correct answer and not the malrule answer — acceptance is code-checked,
zero LLM judges); at *flip sites* (post-targeted-remediation turns),
chosen = the rendered correct turn, rejected = a GLM-generated stubborn
persistence. 6698 sites → 5849 accepted rejected-continuations (hold
4782/5606; flip 1067/1092); classes balanced by downsampling to
1067+1067 = 2134 pairs. Recipe: standard DPO, β=0.1, lr 5e-7, 1 epoch,
global batch 32, policy and reference both initialized from the
same-seed 4k SFT cell. Readout: paired-by-seed diffs vs those SFT cells.

All experiments ran on a shared node using 4×A100-80G; ~54 training runs
(36 EN SFT + 3 14B + 9 zh + 6 DPO) plus 8 prompt-only baselines.

## 6. Results

### 6.1 H1 — trained holding (PASS, 13/13 rows)

Table 1 gives the full grid. Every row's H1 CI excludes 0.

**Table 1 — EN grid, preregistered tests per row.** Hold = per-seed hold
consistency; base = same-size prompt-only baseline; H1 = 3-seed mean diff
[95% t-CI]; H3 = selectivity diff [CI]; H5 = correct-persona accuracy diff
(one-sided; breach iff < −0.05); other = mean 'other' fraction (§6.6).

| size | scale | hold (3 seeds) | base | H1 diff [95% CI] | H1 | H3 diff [95% CI] | H3 | H5 diff | H5 | other |
|------|-------|----------------|------|------------------|----|------------------|----|---------|----|-------|
| 0.6B | 1k  | .217/.226/.206 | .035 | +0.181 [+0.157,+0.206] | PASS | +0.245 [+0.211,+0.279] | PASS | −0.027 | OK | 0.53 |
| 0.6B | 4k  | .397/.420/.438 | .035 | +0.383 [+0.332,+0.434] | PASS | +0.406 [+0.306,+0.507] | PASS | **−0.096** | **BREACH** | 0.46 |
| 0.6B | 16k | .588/.656/.598 | .035 | +0.579 [+0.488,+0.670] | PASS | +0.559 [+0.419,+0.700] | PASS | **−0.062** | **BREACH** | 0.36 |
| 1.7B | 1k  | .264/.264/.280 | .014 | +0.256 [+0.232,+0.279] | PASS | +0.211 [+0.160,+0.262] | PASS | −0.017 | OK | 0.49 |
| 1.7B | 4k  | .477/.448/.461 | .014 | +0.448 [+0.413,+0.484] | PASS | +0.338 [+0.277,+0.398] | PASS | −0.044 | OK | 0.42 |
| 1.7B | 16k | .665/.688/.670 | .014 | +0.661 [+0.631,+0.690] | PASS | +0.516 [+0.464,+0.568] | PASS | −0.017 | OK | 0.31 |
| 4B   | 1k  | .508/.514/.530 | .062 | +0.455 [+0.426,+0.484] | PASS | +0.516 [+0.507,+0.525] | PASS | −0.002 | OK | 0.37 |
| 4B   | 4k  | .708/.698/.670 | .062 | +0.630 [+0.581,+0.679] | PASS | +0.633 [+0.532,+0.733] | PASS | −0.013 | OK | 0.28 |
| 4B   | 16k | .782/.755/.789 | .062 | +0.713 [+0.668,+0.759] | PASS | +0.752 [+0.684,+0.821] | PASS | +0.016 | OK | 0.22 |
| 8B   | 1k  | .665/.648/.661 | .132 | +0.526 [+0.505,+0.548] | PASS | +0.573 [+0.562,+0.583] | PASS | −0.021 | OK | 0.28 |
| 8B   | 4k  | .774/.785/.776 | .132 | +0.646 [+0.632,+0.661] | PASS | +0.669 [+0.628,+0.710] | PASS | +0.004 | OK | 0.21 |
| 8B   | 16k | .821/.817/.832 | .132 | +0.691 [+0.672,+0.711] | PASS | +0.729 [+0.718,+0.741] | PASS | +0.062 | OK | 0.17 |
| 14B  | 4k  | .805/.795/.791 | .309 | +0.488 [+0.471,+0.505] | PASS | +0.622 [+0.585,+0.658] | PASS | +0.020 | OK | 0.20 |

The strongest cell is 8B-16k: hold .823 vs base .132, misaligned flip
.000/.000/.017, and a *positive* H5 diff (+6.2pp — correct-persona accuracy
improves over the base model). Even the 0.6B floor anchor, which the preregistration
allowed to fail H1, passes it.

### 6.2 H2 — scaling

Hold consistency rises with model size at every data scale and with data
at every size, on all rows (Fig. `figs/hold_scaling.png`,
`figs/hold_data_scaling.png`): 0.6B .22→.42→.61, 1.7B .27→.46→.67, 4B
.52→.69→.78, 8B .66→.78→.82 across 1k→4k→16k; and at 4k, .42→.46→.69→
.78→.80 across 0.6B→14B. The preregistered H2 deliverable is these curves
with CIs, not a point claim. The same monotone pattern holds for
selectivity. Notably, the *baseline* also broadly improves with scale
(base hold .035/.014/.062/.132/.309 — non-monotone at the bottom, with
0.6B above 1.7B, but rising steadily from 1.7B up) — prompt-only
misconception enactment gets better
with size — but at 14B it still sits half a unit below its trained
counterpart, and its flipping remains near-indiscriminate (§6.3).

### 6.3 H3 — selective flipping (headline; PASS 13/13 rows)

Figure `figs/selectivity_4k.png` is the central result. At the 4k scale,
trained targeted flip rises .45→.51→.64→.74→.79 across sizes while trained
misaligned and generic flip fall to ≤.04 from 4B up (8B: .011/.018; 14B:
.006/.008); base models flip at .53–.73 under targeted remediation but also
at .40–.76 under *misaligned*
remediation (8B base: .65 vs .59; 14B base: .57 vs .40). The preregistered
H3 test — trained selectivity minus baseline selectivity, 95% CI excluding
0 — passes in all 13 rows (Table 1); at 8B-16k the difference is +0.729
[+0.718,+0.741] with trained selectivity .78.

The turn-resolved view (Fig. `figs/drift_8B_4k.png`) shows the flip is
locked to the remediation event, not to dialogue length: trained P(malrule
answer) rides .75–.85 through probe turns k=0–2, crashes to ≤.04 exactly at
the k=3 targeted-remediation turn, and stays flat (~.75) under misaligned
remediation; on hold dialogues it stays flat at .77–.80 through k=5 while
the base model decays from .21 to .11 under the same scripted pressure.

### 6.4 H4 — Chinese arm (PASS with a guardrail qualification)

zh prompt-only baselines replicate the EN failure mode (hold
.026/.131/.211 at 1.7B/4B/8B; misaligned+generic flip .50–.67). Trained zh
cells (4k, 3 seeds) pass H1 and H3 at all three sizes:

| size | hold (3 seeds) | base | H1 diff [95% CI] | H3 diff [95% CI] | H5 diff | H5 |
|------|----------------|------|------------------|------------------|---------|----|
| 1.7B | .408/.422/.448 | .026 | +0.401 [+0.350,+0.451] | +0.355 [+0.326,+0.383] | **−0.063** | **BREACH** |
| 4B   | .670/.670/.667 | .131 | +0.538 [+0.534,+0.543] | +0.437 [+0.320,+0.553] | −0.039 | OK |
| 8B   | .768/.779/.774 | .211 | +0.563 [+0.549,+0.577] | +0.524 [+0.483,+0.564] | **−0.057** | **BREACH** |

zh hold runs only slightly below EN at matched size (.43/.67/.77 vs
.46/.69/.78), and 'other' fractions match EN to ±.01 — the
language-neutral probe subset held the measurement instrument constant
across arms. The qualification: **the H5 guardrail is systematically
tighter in Chinese** — all sizes negative and larger in magnitude than
their EN counterparts, with 1.7B (−6.3pp) and 8B (−5.7pp) over the 5pp
tolerance (EN breaches only at 0.6B). Holding transfers cross-lingually;
the correct-persona cost is higher in zh. Reported as-is per the
preregistration.

### 6.5 H5 — correct-persona guardrail

From 1.7B up (EN), trained models stay within tolerance at every scale
(8B-4k +0.4pp; 8B-16k +6.2pp, an improvement). **0.6B breaches at 4k
(−9.6pp) and 16k (−6.2pp)**: at the smallest scale, more misconception
data erodes correct-persona accuracy beyond the bar even with the
correct-solving mix-in. This is consistent with the over-application
finding of arXiv:2604.00818 — boundary enforcement via mixed-in correct
examples suffices from 1.7B up but not at 0.6B. A preregistered negative
result, reported as-is (Fig. `figs/guardrail_h5.png`).

### 6.6 Measurement audit: the 'other' bucket

The frozen extractor classifies 17–53% of dialogue-probe responses as
neither malrule nor correct ('other'), falling with size and data scale.
A 30-sample hand read plus a full-bucket containment scan on seed-17 cells
shows that about half of the 8B 'other' mass is **extraction artifacts, not
behavior** (49% by the containment scan; ~57% in the hand read): at 8B-4k,
41% of 'other' responses contain the malrule answer
in the tail (expression/ratio/united-quantity answer forms truncated to a
numeric fragment — "Answer: 2(x² − 25)" extracted as "2"), 8% the correct
answer, leaving true-other ≈11% of all probes (the model inventing a
*different* wrong method). The artifact share grows with model size, so
reported hold rates *understate* large-model holding; both arms are
measured with the same frozen instrument, so H1/H3 differences are
conservative. A per-malrule breakdown (Appendix D) localizes the
artifacts: of the 12 malrules with hold < .50 at 8B-4k, 10 have 'correct'
≈ 0 and 'other' .60–1.00 — unparseable answer forms, not capitulation;
genuine capitulation is confined to 2 malrules, and excluding artifact
rows the per-malrule median hold at 8B is .97. The 14B row replicates
this pattern. The extractor stays frozen per preregistration; a richer
matcher is future work requiring a new preregistration.

### 6.7 DPO on top of SFT: null at 4B, null-to-marginal at 8B

Paired by seed against the same-seed 4k SFT cells (which are also the DPO
inits), 95% t-CI (df=2):

**4B-4k**: every headline metric's paired CI includes 0 — hold +0.001
[−0.054,+0.056], targeted +0.027 [−0.041,+0.096], selectivity +0.026
[−0.031,+0.084]; the only CI excluding 0 is H5 accuracy +0.005
[+0.003,+0.007].

**8B-4k**: hold −0.013 [−0.038,+0.012], selectivity +0.014
[−0.002,+0.031], H5 −0.004 [−0.027,+0.018] all include 0; the only CI
excluding 0 is targeted flip **+0.022 [+0.008,+0.036]**.

With this pair recipe, DPO adds at most a marginal targeted-flip
improvement and nothing detectable elsewhere. Mechanistically this is
unsurprising in hindsight: the SFT cells already sit near the behavior the
pairs encode (mean misaligned flip ≤.04 before DPO), the preference margin
saturates within ~10 steps (reward accuracies →.9), and at lr 5e-7 the
policy barely moves — the maximum per-tensor weight change over the entire
DPO run is ~3×10⁻⁵ (§7). Reported as-is per amendment A-1; we did not
iterate the recipe.

### 6.8 14B anchor

The 14B-4k row ran the full 3 seeds (the preregistration allowed a
reduced-seed anchor). Its most useful reading is the baseline contrast:
the 14B base is qualitatively the best prompt-only student (hold .309,
selectivity +0.157) — evidence that prompt-only enactment improves with
scale — yet it still flips under misaligned remediation at .400. Training
closes exactly this gap: misaligned flip drops to .000–.017 while targeted
flip stays at .79, H5 within tolerance (+2.0pp).

## 7. Engineering notes: verified checkpointing under FSDP

Three checkpoint-corruption incidents shaped the training harness; we
record them because all three produced *silently* wrong weights that
passed naive checks. Only one was caught by an automated gate — (2), by
the save-time empty-tensor refusal and disk-verify pass; (1) was caught by
manual forensics during pre-grid smoke testing, and (3) by a human
noticing degenerate DPO evals and diffing the checkpoint against its init.
Had (3) gone uncaught it would have shipped a corrupted DPO table (§6.7);
the headline SFT tables were produced under the already-hardened save
path.

1. **D2H gather race.** Under real workload backlog, an FSDP
   FULL_STATE_DICT gather with CPU offload could copy stale shard data for
   the *last* FSDP unit (deterministically reproducible; bit-identical
   corruption across runs). Mitigation: explicit device synchronization
   around the gather plus a post-save verify.
2. **A pre-save canary that poisoned the save.** A "live generation"
   sanity check before saving materialized the full model via
   `summon_full_params`; at 14B this deterministically OOMs mid-unshard
   and leaves one FSDP unit's parameter views empty, corrupting *every*
   subsequent state-dict path identically — including the "independent"
   verification path, which shares the same hooks. All three 14B
   checkpoints were holed at the same 4 tensors before the cause was
   found. Fix: nothing may touch FSDP state between training and the
   gather; the canary runs after save+verify; the save refuses to write
   any empty gathered tensor; verification is redefined as disk
   write-fidelity (reload every saved tensor and compare) plus a cold-load
   generation check.
3. **An unguarded second save path.** The DPO trainer had its own save
   code that never received fix (1); the race corrupted the last unit of
   all three first-generation 8B DPO checkpoints (layer-35 tensors off by
   2.6–17.6 where healthy DPO drift is ~10⁻⁵–10⁻³). The corrupted
   checkpoints produced degenerate evals that could have been mistaken
   for a behavioral result. Beyond porting the hardened save, we added a
   *semantic* gate: a DPO final whose weights drift more than 0.5 from its
   SFT init fails the cell. All three cells were retrained under the
   hardened path (worst observed drift 3×10⁻⁵).

Lessons: (a) FSDP checkpoint saves need a synchronized, verified gather
*and* a task-level semantic gate; (b) a 2-prompt generation spot check is
blind to value corruption — it passed a checkpoint whose evals were
degenerate; (c) run sanity probes that can fail destructively *after* the
artifact is safely on disk. 14B full fine-tuning on 4×A100-80G is feasible
(~85 min per train+eval cell) with the expandable-segments allocator and
the DCP-based save.

## 8. Limitations

- **Extractor truncation.** The frozen extractor undercounts holding for
  expression-form answers (§6.6); we keep it frozen per preregistration
  and report the artifact quantitatively instead of patching it post-hoc.
- **0.6B guardrail breach.** At the smallest scale, holding is bought with
  correct-persona degradation beyond the preregistered bar.
- **zh guardrail cost.** The correct-persona cost is systematically higher
  in Chinese (two of three sizes breach), qualifying H4.
- **Coverage.** 100 of MalruleLib's 102 malrules, middle-school
  arithmetic/algebra; probe
  answers restricted to language-neutral forms in zh; misconceptions are
  enacted one-at-a-time (no compound misconceptions).
- **Style monoculture.** All tutor prose is GLM-rendered; simulators may
  be tuned to one tutoring voice.
- **Scale ceiling.** 14B was the largest size feasible on the available
  node; the 4k-only 14B row limits the size×data interaction readout at
  the top end.
- **No human-tutor study.** We measure the trained policy against
  scripted, code-verified conditions; usefulness for live tutor training
  is not evaluated here.

## 9. Release, license, and ethics

We release: generator and rendering code, training/eval harness, rendered
dialogues (EN + zh), frozen probe sets with SHA-256 digests, all
preview/aggregate results, analysis scripts, figures, the preregistration
(PLAN v1.0 at `8c1fe4b` plus dated amendments), and the decision log
D-001–D-027 recording every incident and deviation transparently.
Checkpoint release is exemplar-based: the kept cells (EN 4B-4k, 8B-4k,
8B-16k, 14B-4k SFT and 8B DPO, all 3 seeds each, plus surviving single-seed
4B-DPO and zh-8B exemplars), hosted on ModelScope at
`ZhaoKevin/holdfast-qwen3-student-simulators` — the remaining cells'
final weights were deleted under disk pressure during the run window
(D-020) and are exactly reproducible from the frozen recipe, seeds, and
released data. Released copies of infrastructure-adjacent files (decision
log, plan, harness comments) are redacted only for internal infrastructure
identifiers (hostnames, gateway addresses); no scientific content is
altered (D-027).

MalruleLib (Chen, Liu & Sonkar) is distributed under its custom
non-commercial share-alike license; our derived data and generators
inherit it. Trained checkpoints are released for non-commercial research
use with attribution (Qwen3 bases are Apache-2.0). Per the MalruleLib
license, no MalruleLib-derived content is used to train, fine-tune, or
*evaluate* any commercial or closed-source model, anywhere in this project;
GLM is used strictly as a generation-side drafting tool and no performance
claims about it are made or implied.

Misconception simulators are dual-use in a narrow sense: a model trained
to be convincingly wrong could, out of context, spread wrong math. The
mitigations are inherent to the design — the misconception is
prompt-assigned (the same checkpoint acts as a correct student under the
correct persona, H5), the domain is middle-school arithmetic with
code-computable ground truth, and the release documents the intended
tutor-training use.

## References

- Chen, Liu & Sonkar. *MalruleLib* (arXiv:2601.03217; ACL Main 2026).
  https://github.com/sonkar-lab/malrulelib
- Sonkar group. *Misconception acquisition dynamics in language models.*
  arXiv:2604.00818.
- Sonkar group. *Simulating Students or Sycophantic Problem Solving?*
  (Selective Flip Score.) arXiv:2605.12748.
- Rafailov et al. *Direct Preference Optimization.* arXiv:2305.18290.
- Qwen team. *Qwen3 Technical Report.* arXiv:2505.09388.

*(Author-form citations for the two "Sonkar group" entries to be completed
from the arXiv pages at publication time; numbers above are frozen.)*

## Appendices

- **A. Full grid tables** — `docs/results_interim_20260826.md` (all rows,
  per-seed values, CIs; source of every number in §6).
- **B. Prompts** — `docs/appendix_b_prompts.md` (AST-extracted from the
  harness; code is the source of truth).
- **C. Audit protocols and samples** — zh 100-probe translation audit;
  'other' 30-sample hand read (archived rng-seeded samples).
- **D. Per-malrule breakdowns** — `docs/appendix_d_8B_4k.md`,
  `appendix_d_0.6B_4k.md`, `appendix_d_14B_4k.md`,
  `appendix_d_zh_8B_4k.md`, `appendix_d_dpo_8B_4k.md`.
