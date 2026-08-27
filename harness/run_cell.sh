#!/bin/bash
# HoldFast grid cell runner: one whole-node job = train one cell, then eval it.
#   usage: run_cell.sh SIZE SCALE SEED [NGPU]        e.g. run_cell.sh 4B 4k 17
# SIZE in {0.6B,1.7B,4B,8B,14B}; SCALE in {1k,4k,16k}; NGPU defaults to 8.
# Eval = probe_eval dialogue mode + static x2 personas, sharded across NGPU
# GPUs (protocol-neutral: probe draws are per-dialogue-seeded). Analysis merges
# shard files. Baseline evals: run_baseline.sh (same harness, base checkpoint).
set -euo pipefail
SIZE=$1; SCALE=$2; SEED=$3; NGPU=${4:-8}
ROOT=${HOLDFAST_ROOT:-/data/holdfast}
# zh arm (D-015): HOLDFAST_LANG=zh -> zh- cell prefix + zh train/eval data
ARM=${HOLDFAST_LANG:-en}
CELL=${ARM}-${SIZE}-${SCALE}-s${SEED}
if [ "$ARM" = "zh" ]; then
  RENDERED=$ROOT/data/main/rendered_zh.jsonl
  SCAFFOLDS=$ROOT/data/main/scaffolds_${SCALE}_zh.jsonl
else
  RENDERED=$ROOT/data/main/rendered_main.jsonl
  SCAFFOLDS=$ROOT/data/main/scaffolds_${SCALE}.jsonl
fi
OUT=$ROOT/runs/grid/$CELL
mkdir -p "$OUT/eval"
cd "$ROOT"

# disk guard: a near-full yrfs PVC once silently corrupted the last-written
# tensors of a checkpoint (see DECISIONS) — refuse to start without headroom
FREE_G=$(df -Pk "$ROOT" | awk 'NR==2 {print int($4/1048576)}')
if (( FREE_G < 100 )); then
  echo "only ${FREE_G}G free under $ROOT — refusing to start" >&2; exit 3
fi

case $SIZE in                       # per-size hyperparams (frozen at prereg)
  0.6B|1.7B) MICRO=4; LR=2e-5; EXTRA="" ;;
  4B)        MICRO=2; LR=2e-5; EXTRA="" ;;
  8B)        MICRO=2; LR=1e-5; EXTRA="--fsdp" ;;
  14B)       MICRO=1; LR=1e-5; EXTRA="--fsdp"
             # 14B FSDP OOM'd by ~0.5G at step 1 with ~1G reserved-unallocated
             # (2026-08-26); allocator-only change, no training-math effect
             export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True ;;
  *) echo "unknown SIZE $SIZE" >&2; exit 2 ;;
esac

if [ ! -e "$OUT/final/config.json" ]; then
  torchrun --nproc_per_node="$NGPU" harness/train_sft.py \
    --model "$ROOT/models/Qwen3-$SIZE" \
    --rendered "$RENDERED" \
    --scaffolds "$SCAFFOLDS" \
    --out "$OUT" --seed "$SEED" --lr "$LR" --micro-batch "$MICRO" \
    --epochs 2 --global-batch 32 $EXTRA 2>&1 | tee "$OUT/train.log"
fi
[ -e "$OUT/final/config.json" ] || { echo "train failed: no final ckpt" >&2; exit 1; }

# D-016: refuse to hand a degenerate/corrupt checkpoint to eval
python harness/gen_check.py "$OUT/final" 2>&1 | tee "$OUT/gen_check.log"

bash "$ROOT/harness/eval_ckpt.sh" "$OUT/final" "$OUT/eval" "$NGPU"
echo "CELL DONE -> $OUT"
