# HoldFast 执迷

**Can small open models be trained to *hold* a math misconception through a full
tutoring dialogue — and let go only when the tutoring is actually right?**

HoldFast trains Qwen3 student simulators (0.6B–14B) that stably enact an assigned
mathematical misconception (malrule) across multi-turn tutoring dialogues, verified
turn-by-turn with **code-computed probes** from executable malrules — zero LLM judges
in headline metrics. The headline control is **selective flipping**: a faithful student
simulator must update its belief under targeted, correct remediation (a simulator that
never yields is a stubbornness artifact, preregistered as a failure condition).

**Status: v1.0 — all preregistered experiments complete (2026-08-27).**
Full paper draft: [`docs/PAPER.md`](docs/PAPER.md). Every number comes from the
frozen preregistered harness ([`docs/PLAN.md`](docs/PLAN.md), frozen before any
main-grid run; decision log [`docs/DECISIONS.md`](docs/DECISIONS.md)).

## Headline results

3 training seeds per cell; tests are 3-seed mean differences vs the same-size
prompt-only baseline with 95% t-CIs. Selectivity = targeted flip −
max(misaligned, generic flip).

| | hold | targeted flip | misaligned flip | selectivity vs base |
|---|---|---|---|---|
| Qwen3-8B prompt-only | .13 | .65 | .59 | — |
| Qwen3-8B SFT (16k) | **.82** | .79 | .00–.02 | **+0.73** [+0.72,+0.74] |
| Qwen3-14B prompt-only | .31 | .57 | .40 | — |
| Qwen3-14B SFT (4k) | **.80** | .79 | .00–.02 | **+0.62** [+0.59,+0.66] |

- **H1 (trainability)**: PASS on all 13 grid rows (0.6B–14B × 1k/4k/16k).
- **H2 (scaling)**: hold rises monotonically with size and data on every row.
- **H3 (selective flipping, headline)**: PASS on all 13 rows — trained models
  flip exactly when remediation targets their misconception; bases flip
  near-indiscriminately.
- **H4 (Chinese arm)**: replicates at 1.7B/4B/8B, with a tighter correct-persona
  guardrail (two preregistered breaches, reported as-is).
- **H5 (guardrail)**: within 5pp from 1.7B up (EN); 0.6B breaches (preregistered
  negative result).
- **DPO on top of SFT**: null at 4B, null-to-marginal at 8B (reported as-is).

## Repo map

```
docs/PLAN.md          preregistration (frozen v1.0 + dated amendments)
docs/DECISIONS.md     decision log D-001..D-027 (method choices + infra forensics)
docs/PAPER.md         paper draft (single source: docs/results_interim_20260826.md)
docs/figs*/           scaling / selectivity / guardrail / drift figures
docs/appendix_*.md    prompts + per-malrule breakdowns
harness/              everything executable:
  gen_scaffolds.py, render_dialogues.py, translate_zh.py, make_zh_data.py   data pipeline
  build_probes.py, probe_eval.py, answer_eq.py, aggregate.py               frozen eval
  train_sft.py, train_dpo.py, make_dpo_pairs.py                            training
  run_cell.sh, run_baseline.sh, run_dpo_cell.sh, eval_ckpt.sh              orchestration
  gen_check.py, ckpt_diff_gate.py, fsdp_save_test.py                       integrity gates
  row_ci.py, dpo_ci.py, per_malrule.py, plot_scaling.py                    analysis
data/                 scaffolds, rendered dialogues (EN/zh), frozen probe sets
                      (SHA-256 pinned), DPO pairs, audit samples
runs_mirror/          per-run eval previews (aggregate metrics) for every cell
                      and baseline in the paper
```

Reproduce a paper row locally: `python3 harness/row_ci.py 8B 16k --runs runs_mirror`
(or `dpo_ci.py 8B --runs runs_mirror`).

## Method in one paragraph

A scaffold generator draws problems from MalruleLib's executable malrules and
precomputes all student math (malrule answers/steps, correct answers/steps);
an LLM renders *prose only*, hard-checked turn-by-turn against the scaffold
(answer containment + leak bans, ≤3 attempts then drop). Evaluation forks a
probe problem after every on-policy student turn of held-out dialogues and
classifies the answer with a frozen deterministic extractor/comparator
({malrule, correct, other}) — no LLM judges anywhere in headline metrics.
See `docs/PAPER.md` §3–4.

## Released artifacts

Code, generators, rendered dialogues (EN + zh), frozen probe sets, DPO pairs,
eval previews, figures, and the full prereg/decision history are in this repo.
Checkpoint exemplars — one seed (s17) per kept cell family: EN 4B-4k /
8B-4k / 8B-16k / 14B-4k SFT, 8B-DPO and 4B-DPO, and zh-8B; 7 checkpoints in
consolidated HF format, each md5-verified against the training-node copy —
are hosted on ModelScope:
[ZhaoKevin/holdfast-qwen3-student-simulators](https://modelscope.cn/models/ZhaoKevin/holdfast-qwen3-student-simulators).
The other two seeds of each 3-seed cell are not hosted (transfer budget,
D-028) and are exactly reproducible from the frozen recipe, seeds, and
released data; every paper number is a 3-seed mean whose per-seed eval
previews are in `runs_mirror/`.
Code mirror: [Gitee](https://gitee.com/zty552252kevin/holdfast).

## License notes

- **MalruleLib** (Chen, Liu & Sonkar, [arXiv:2601.03217](https://arxiv.org/abs/2601.03217),
  ACL Main 2026; [repo](https://github.com/sonkar-lab/malrulelib), pinned `8ddedfb`;
  102 executable malrules across 22 categories, 100 used here) is distributed
  under its own **non-commercial share-alike license**. Derived data and
  generators in this project inherit that license.
- **Trained checkpoints** are released for **non-commercial research use with
  attribution**; Qwen3 base weights are Apache-2.0 (respect both).
- This project does **not** use MalruleLib content to train, fine-tune, or
  evaluate any commercial/closed-source LLM, and this restriction carries to
  downstream use of the released data.
- See [`LICENSE`](LICENSE) for the component-by-component terms.

## Citation

```bibtex
@misc{zhao2026holdfast,
  title  = {HoldFast: Training Small Open Models to Hold Assigned Math
            Misconceptions Through Multi-Turn Tutoring --- and to Yield
            Only to Targeted Remediation},
  author = {Zhao, Kevin},
  year   = {2026},
  url    = {https://github.com/zty552252kevin-code/holdfast}
}
```

Please also cite MalruleLib (Chen, Liu & Sonkar, arXiv:2601.03217).
