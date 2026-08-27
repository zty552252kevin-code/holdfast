#!/bin/bash
# HoldFast: prompt-only baseline eval for one base model (same frozen harness,
# same probes, same eval dialogues — only the checkpoint differs).
#   usage: run_baseline.sh SIZE [NGPU]      e.g. run_baseline.sh 4B
set -euo pipefail
SIZE=$1; NGPU=${2:-8}
ROOT=${HOLDFAST_ROOT:-/data/holdfast}
# zh arm (D-015): HOLDFAST_LANG=zh -> zh- prefix; eval_ckpt.sh swaps zh data
OUT=$ROOT/runs/baselines/${HOLDFAST_LANG:-en}-${SIZE}-base
mkdir -p "$OUT"
bash "$ROOT/harness/eval_ckpt.sh" "$ROOT/models/Qwen3-$SIZE" "$OUT" "$NGPU"
echo "BASELINE DONE -> $OUT"
