#!/bin/bash
# HoldFast DPO cell runner (Amendment A-1): DPO on top of the same-size
# same-seed 4k SFT cell, then the frozen eval.
#   usage: run_dpo_cell.sh SIZE SEED [NGPU]      e.g. run_dpo_cell.sh 4B 17 4
# SIZE in {4B,8B} (A-1 scope); pairs file: data/dpo/pairs_en_4k.jsonl.
set -euo pipefail
SIZE=$1; SEED=$2; NGPU=${3:-4}
ROOT=${HOLDFAST_ROOT:-/data/holdfast}
SFT=$ROOT/runs/grid/en-${SIZE}-4k-s${SEED}/final
PAIRS=$ROOT/data/dpo/pairs_en_4k.jsonl
[ -e "$SFT/config.json" ] || { echo "missing SFT ckpt $SFT" >&2; exit 2; }
[ -s "$PAIRS" ] || { echo "missing pairs $PAIRS" >&2; exit 2; }
OUT=$ROOT/runs/grid/en-dpo-${SIZE}-4k-s${SEED}
mkdir -p "$OUT/eval"
cd "$ROOT"

FREE_G=$(df -Pk "$ROOT" | awk 'NR==2 {print int($4/1048576)}')
if (( FREE_G < 100 )); then
  echo "only ${FREE_G}G free under $ROOT — refusing to start" >&2; exit 3
fi

case $SIZE in                 # A-1: recipe frozen (beta .1, lr 5e-7, 1 epoch)
  4B) MICRO=1; EXTRA="" ;;
  8B) MICRO=1; EXTRA="--fsdp --precompute-ref" ;;
  *) echo "SIZE $SIZE outside A-1 scope {4B,8B}" >&2; exit 2 ;;
esac

if [ ! -e "$OUT/final/config.json" ]; then
  torchrun --nproc_per_node="$NGPU" harness/train_dpo.py \
    --model "$SFT" --pairs "$PAIRS" \
    --out "$OUT" --seed "$SEED" --micro-batch "$MICRO" \
    --global-batch 32 $EXTRA 2>&1 | tee "$OUT/train.log"
fi
[ -e "$OUT/final/config.json" ] || { echo "dpo train failed: no final ckpt" >&2; exit 1; }

# D-025 drift gate: DPO at lr 5e-7 must stay within a whisker of its init;
# the D-016 stale-shard race (hit all three first 8B cells) fails this hard
python3 harness/ckpt_diff_gate.py "$OUT/final" "$SFT" --max-diff 0.5 \
  2>&1 | tee "$OUT/diff_gate.log"

python harness/gen_check.py "$OUT/final" 2>&1 | tee "$OUT/gen_check.log"

bash "$ROOT/harness/eval_ckpt.sh" "$OUT/final" "$OUT/eval" "$NGPU"
echo "DPO CELL DONE -> $OUT"
