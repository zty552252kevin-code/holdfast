# Interim results — EN grid, 2026-08-26 morning

Status snapshot after the first night of grid runs on the shared devbox
(4×A100-80G, GPUs 4-7; node shape per DECISIONS D-017). **34/34 chain jobs
exited rc=0; every checkpoint passed the D-016 gates (live-gen, exact tensor
verify, cold gen-check).**

Completed: the FULL EN grid — {0.6B, 1.7B, 4B, 8B} × {1k, 4k, 16k},
3 seeds each (17/1017/2017, D-017), all four prompt-only baselines, the zh
arm (chain #5), the DPO arm 4B+8B (chain #6/#9), and the 14B-4k anchor row
(chain #8, full 3 seeds + 14B baseline) — grid complete as of 07:54 Beijing
8/27. Eval
decoding seed 7 everywhere (D-014). 8B-4k cells ran ~31 min each on 4 GPUs;
14B-4k cells ~85 min each (expandable_segments + DCP save, D-024).

All numbers from the frozen harness (probe_eval + aggregate, prereg 8c1fe4b);
tests as preregistered in PLAN.md §2: 3-seed mean diff vs the same-size
prompt-only baseline, 95% t-CI (df=2, t=4.303) excluding 0; H5 tolerance
5pp absolute.

## Preregistered tests, per row

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

(H3 column: selectivity(trained) − selectivity(baseline); baseline
selectivities: 0.6B −0.089, 1.7B +0.053, 4B −0.028, 8B +0.052, 14B +0.157.
14B anchor (chain8, full 3 seeds, retrained after D-024): trained sel
.780/.793/.764, misaligned flip .000–.017, H5 .675/.688/.693 vs base .665;
base 14B is the strongest prompt-only model (hold .309, sel +0.157) and the
trained gap still clears it by half a unit. Size-monotone hold at 4k extends:
.42 → .46 → .69 → .78 → .80. 8B-16k
trained selectivity .780/.776/.786 — the strongest cell on every axis:
hold .823 mean, misaligned flip .000, H5 +0.062 (correct-persona acc
IMPROVES over base at 16k), other down to .17.
"other" = mean fraction of dialogue-probe responses the frozen extractor
classified as neither malrule nor correct — auxiliary, hand-spot-check
pending per prereg.)

## Readings (interim, EN arm)

1. **H1 and H3 pass in all 11 completed rows** with CIs excluding 0 — even
   the 0.6B floor anchor, which the prereg allowed to fail.
2. **H2 direction confirmed on both axes**: hold-consistency rises
   monotonically with model size at every data scale, and with data scale at
   every size (0.6B: .22→.42→.61; 1.7B: .27→.46→.67; 4B: .52→.69→.78 across
   1k→4k→16k; 8B: .66→.78 across 1k→4k). Same monotone pattern for
   selectivity. 8B-4k is the strongest completed cell (hold .778, trained
   selectivity ≈.72, H5 +0.4pp). Formal H2 statement is curves + CIs, not a
   test; plots at aggregation time.
3. **Preregistered negative result: 0.6B breaches the H5 collateral-damage
   tolerance at 4k (−9.6pp) and 16k (−6.2pp)** — at 0.6B, scaling up
   misconception training data erodes correct-persona accuracy beyond the 5pp
   bar. 1.7B and 4B stay within tolerance at every scale (1.7B-16k −1.7pp,
   4B-16k +1.6pp). Reads as an over-application boundary failure specific to
   the smallest model, consistent with arXiv:2604.00818's finding that
   misconception training over-applies unless boundaries are enforced —
   here the correct-persona mix-in suffices from 1.7B up but not at 0.6B.
   Reported as-is per prereg §7.
4. The extractor 'other' fraction falls with both size and data scale
   (0.53 → 0.22): larger/better-trained simulators produce more extractable
   answers. Hand spot-check of 'other' responses still owed (aux item).

Raw per-row metrics: `preview.json` in each run's eval dir on the devbox
(runs/grid/en-*/eval/, runs/baselines/en-*-base/).

## zh arm data (D-015/D-019) — render yields

- Translations: 12,701/12,701 unique strings (100%), mechanical verbatim-math
  check; 100/100 hand-audit sample clean (bar >=98%, D-019).
- zh eval renders: 319/327 (97.6%; EN eval: 318/327).
- zh main renders (4k): 3867/4001 (96.65%; EN main 4k subset: 3923/4001 =
  98.05% — an earlier draft of this line said 3865, a mid-render snapshot;
  per-cell train logs confirm every EN 4k cell trained on 3923. Corrected
  2026-08-27, D-027.)
  -> zh-4k cells train on 3867 rendered dialogues.
- Same renderer, same hard checks (answer containment / leak bans), GLM via
  institutional gateway; failures are check-rejections after 3 attempts, same
  policy as EN.

### zh prompt-only baselines (H4 control; chain #5, 2026-08-26)

| base | hold | targeted | misaligned | generic | selectivity | H5 acc |
|---|---|---|---|---|---|---|
| zh-1.7B | .026 | .676 | .667 | .648 | +0.010 | .659 |
| zh-4B | .131 | .759 | .623 | .616 | +0.136 | .681 |
| zh-8B | .211 | .694 | .518 | .504 | +0.177 | .726 |

(n: hold 625, targeted 170, misaligned 114, generic 250, H5 879 — zh probe
subset per D-019.) Reading: the EN failure mode replicates cross-lingually —
prompt-only bases barely hold (.03–.21) and flip near-indiscriminately
(misaligned/generic flip .50–.67). zh bases hold somewhat more than EN bases
at the same size (zh-4B .131 vs EN-4B .062; zh-8B .211 vs EN-8B .132) but
remain far below trained levels.

### zh trained rows (H4; chain #5 complete, 2026-08-26 17:55 Beijing)

| size | scale | hold (s17/s1017/s2017) | base | H1 diff [95% CI] | H1 | H3 diff [95% CI] | H3 | H5 diff | H5 | other |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.7B | 4k | .408/.422/.448 | .026 | +0.401 [+0.350,+0.451] | PASS | +0.355 [+0.326,+0.383] | PASS | **−0.063** | **BREACH** | 0.41 |
| 4B | 4k | .670/.670/.667 | .131 | +0.538 [+0.534,+0.543] | PASS | +0.437 [+0.320,+0.553] | PASS | −0.039 | OK | 0.28 |
| 8B | 4k | .768/.779/.774 | .211 | +0.563 [+0.549,+0.577] | PASS | +0.524 [+0.483,+0.564] | PASS | **−0.057** | **BREACH** | 0.21 |

(base selectivity: 1.7B +0.010, 4B +0.136, 8B +0.177; trained sel 1.7B
.373/.369/.352, 4B .518/.595/.604, 8B .718/.686/.697.) Notes: (a) **H1/H3
transfer to zh at all three sizes** — trained zh-8B holds .774 vs base .211
and flips targeted .74 vs misaligned .04 (fig figs_zh/selectivity_4k); (b)
**the H5 guardrail is systematically tighter in zh**: every zh size is
negative and larger in magnitude than its EN counterpart, with 1.7B
(−6.3pp) and 8B (−5.7pp) over the 5pp tolerance and 4B (−3.9pp) within —
EN breaches only at 0.6B. Reported as-is per prereg §7; the H4 transfer
claim (H1/H3) stands, qualified by the higher correct-persona cost; (c) zh
hold runs slightly below EN at matched size/scale (1.7B .43 vs EN .46; 4B
.67 vs EN .69; 8B .77 vs EN .78) — no large cross-lingual gap; (d) 'other'
fractions match EN almost exactly (.41/.28/.21 vs EN .42/.28/.21) — the
language-neutral probe subset (D-019) held extraction difficulty constant
across arms as designed. Figures: figs_zh/ (hold, selectivity, guardrail,
drift). Trained zh rows: pending chain #5 cells.

## DPO arm (A-1) — pair construction (2026-08-26 12:18)

Sites from the frozen 4k EN rendered dialogues: 6698 (hold 5606, flip 1092;
caps hold<=2/flip<=1 per dialogue, leak-exempt sites skipped). GLM rejected-
continuation generation (institutional gateway, generation-side only; acceptance is
code-checked containment — zero LLM judges): accepted 5849, dropped 849
after <=3 attempts each. Per class: hold 4782/5606 accepted (14.7% dropped —
the model resists writing a clean premature capitulation that names the
correct answer without echoing the malrule answer), flip 1067/1092 (2.3%
dropped). Attempts distribution: 1x 5738, 2x 73, 3x 38. Balanced by
downsampling hold (rng "dpo-pairs-v1"): 1067+1067 = 2134 pairs ->
data/dpo/pairs_en_4k.jsonl (synced to devbox). Training: chain6 tonight
(en-dpo-{4B,8B}-4k-s{17,1017,2017}, init from same-seed SFT cells).

### DPO vs SFT, 4B-4k (A-1 readout; chain #6, 2026-08-26 20:35 Beijing)

Paired by seed (same-seed SFT cell is both the init and the comparator);
3 seeds, 95% t-CI df=2:

| metric | SFT (3 seeds) | DPO (3 seeds) | paired diff [95% CI] |
|---|---|---|---|
| hold | .708/.698/.670 | .683/.709/.686 | +0.001 [−0.054,+0.056] |
| targeted | .604/.676/.648 | .659/.703/.648 | +0.027 [−0.041,+0.096] |
| misaligned | .042/.033/.025 | .042/.033/.017 | −0.003 [−0.015,+0.009] |
| generic | .045/.042/.027 | .057/.019/.027 | −0.004 [−0.047,+0.039] |
| selectivity | .559/.634/.622 | .603/.670/.622 | +0.026 [−0.031,+0.084] |
| H5 acc | .636/.637/.642 | .641/.641/.648 | **+0.005 [+0.003,+0.007]*** |

Reading: **at 4B, DPO on top of SFT is a null result** — every headline
metric's paired CI includes 0; the only CI excluding 0 is a +0.5pp
correct-persona accuracy gain, too small to matter. Direction is mildly
positive (targeted +2.7pp, selectivity +2.6pp, misaligned/generic not
worsened) but not resolvable at 3 seeds. Reported as-is per A-1.
Eval integrity: DPO cells' per-bucket n's match the same-seed SFT cells
exactly (660/182/120/264/1000). Note: all three *first-generation* 8B DPO
checkpoints were corrupted at save time (D-016 stale-shard race in
train_dpo.py's then-unguarded gather; layer 35) — those evals are
quarantined (runs_mirror/invalid_d025/) and the cells below are the D-025
retrains under the hardened save path + drift gate (worst drift 3e-5,
all gates PASS). 4B cells were unaffected (non-FSDP save path).

### DPO vs SFT, 8B-4k (A-1 readout; chain #9 retrain, 2026-08-27 07:54 Beijing)

| metric | SFT (3 seeds) | DPO (3 seeds) | paired diff [95% CI] |
|---|---|---|---|
| hold | .774/.785/.776 | .773/.765/.758 | −0.013 [−0.038,+0.012] |
| targeted | .758/.731/.725 | .775/.753/.753 | **+0.022 [+0.008,+0.036]*** |
| misaligned | .008/.017/.008 | .017/.017/.017 | +0.006 [−0.006,+0.018] |
| generic | .019/.023/.011 | .027/.023/.027 | +0.008 [−0.011,+0.026] |
| selectivity | .739/.708/.714 | .748/.730/.726 | +0.014 [−0.002,+0.031] |
| H5 acc | .678/.671/.687 | .668/.677/.678 | −0.004 [−0.027,+0.018] |

Reading: **at 8B the DPO arm is null-to-marginal, consistent with 4B** —
the only CI excluding 0 is a +2.2pp targeted-flip gain
[+0.008,+0.036]; hold, selectivity, and H5 paired CIs all include 0
(selectivity +0.014 [−0.002,+0.031] just barely). Same mechanism reading
as 4B: the SFT cells already sit near the behavior the pairs encode, and
at lr 5e-7 the policy barely moves (drift gate: max weight change 3e-5).
Reported as-is per A-1.

## 'other' bucket hand audit (aux, per prereg §aux-checks)

Question: does the ~20% 'other' fraction hide misclassified hold/correct
behavior? Audit on completed cells (dialogue mode, all probe types), seed-17
cells; 30-sample hand read (rng "other-audit-D0", archived at
data/audits/other_audit_8B4k_s17_sample30.json) + full-bucket containment
estimate (same bounded-match containment as the renderer QC, on the last
400 chars of each 'other' response):

| cell | other n | tail contains malrule-only | contains correct-only | residual true-other |
|---|---|---|---|---|
| en-8B-4k-s17   | 369 (21.9%) | 150 (41%) | 30 (8%) | 189 (51%) |
| en-4B-4k-s17   | 482         |  96 (20%) | 36 (7%) | 350 (73%) |
| en-1.7B-4k-s17 | 685         |  78 (11%) | 51 (7%) | 556 (81%) |

Hand read (30/30 reviewed) agrees: ~57% of 8B 'other' are **extraction
artifacts**, not behavioral 'other' — the frozen extractor keeps a numeric
fragment when the stated answer is an expression/ratio/united/phrase form
("Answer: 2(x² - 25)" → extracted "2"; "7:8" → "7"; "5.0 feet" vs "5.0";
no-cue tail "…is 9.0 × 10^10 bytes" → last-numeric fallback grabs the
exponent "10"). The rest are genuine 'other': the model invents a *different*
wrong method (its own miscomputation, not the assigned malrule).

Reading: the frozen instrument **undercounts** both hold (artifact-malrule)
and correct (artifact-correct); trained models and prompt-only baselines are
measured with the same instrument, so H1/H3 diffs are conservative, not
inflated. True 'other' at 8B is ≈11% of probes, and the artifact share GROWS
with model size (bigger models hold in expression-style answers more often),
so reported hold rates understate large-model holding the most. No protocol
change (extractor is frozen per prereg); recorded for the writeup.
