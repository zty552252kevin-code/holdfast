#!/bin/bash
# HoldFast: evaluate one checkpoint with the frozen probe harness.
#   usage: eval_ckpt.sh CKPT_DIR OUT_DIR [NGPU]
# Runs probe_eval in all 3 modes (dialogue / static misconception persona /
# static correct persona), sharded across NGPU GPUs. Sharding is protocol-
# neutral (probe draws seeded per dialogue_id). Merge shards in analysis.
# Used for grid cells (run_cell.sh) AND prompt-only baselines (base ckpt).
set -euo pipefail
CKPT=$1; OUT=$2; NGPU=${3:-8}
ROOT=${HOLDFAST_ROOT:-/data/holdfast}
mkdir -p "$OUT"
cd "$ROOT"

# GPU binding: HOLDFAST_GPUS="4,5,6,7" maps shard i -> i-th listed GPU
# (the shared devbox only has GPUs 4-7 free; grid nodes use the default 0..N-1)
# fallback order: HOLDFAST_GPUS > inherited CUDA_VISIBLE_DEVICES > 0..N-1
# (child CUDA_VISIBLE_DEVICES REPLACES the parent binding, so listing
# physical ids here is required on the shared box — GPUs 0-3 are not ours)
IFS=',' read -ra GPUS <<< "${HOLDFAST_GPUS:-${CUDA_VISIBLE_DEVICES:-$(seq -s, 0 $((NGPU-1)))}}"

# zh arm (D-015): HOLDFAST_LANG=zh swaps in the zh eval data + zh templates
LANG_ARGS=()
if [ "${HOLDFAST_LANG:-en}" = "zh" ]; then
  LANG_ARGS=(--lang zh
    --rendered "$ROOT/data/eval/rendered_eval_zh.jsonl"
    --scaffolds "$ROOT/data/eval/scaffolds_eval_zh.jsonl"
    --probes-hold "$ROOT/data/probes/probes_hold_zh.jsonl"
    --probes-correct "$ROOT/data/probes/probes_correct_zh.jsonl")
fi

run_shards() {  # run_shards <tag> <extra probe_eval args...>
  local tag=$1; shift
  local pids=()
  for ((s=0; s<NGPU; s++)); do
    CUDA_VISIBLE_DEVICES=${GPUS[$s]} python3 harness/probe_eval.py --model "$CKPT" \
      "$@" "${LANG_ARGS[@]}" --shard "$s/$NGPU" --out "$OUT/${tag}.shard${s}.jsonl" \
      > "$OUT/${tag}.shard${s}.log" 2>&1 &
    pids+=($!)
  done
  # bare `wait` always returns 0 — it silently swallowed 12 shard OOMs on
  # 2026-08-26 (D-023); wait each pid so a shard failure fails the cell
  local rc=0
  for p in "${pids[@]}"; do wait "$p" || rc=1; done
  (( rc == 0 )) || { echo "shard failure in $tag (see $OUT/${tag}.shard*.log)" >&2; exit 1; }
}

run_shards dialogue   --mode dialogue
run_shards static_mis --mode static --persona misconception
run_shards static_cor --mode static --persona correct
echo "EVAL DONE -> $OUT"
