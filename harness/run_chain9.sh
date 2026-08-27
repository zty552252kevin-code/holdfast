#!/bin/bash
# chain9: retrain ALL THREE 8B DPO cells under the hardened train_dpo.py
# (D-025: the unguarded legacy gather hit the D-016 stale-shard race in all
# three first saves — layer 35 corrupt; every 8B DPO eval invalidated).
# Waits for chain8 (14B retrains) to release GPUs 4-7, then runs the cells;
# run_dpo_cell.sh now applies the drift gate + gen_check + eval per cell.
cd /data/holdfast
S=runs/chain9_20260827.status
echo "$(date '+%F %T') CHAIN9 waiter: polling for CHAIN8 COMPLETE" >> "$S"
until grep -q "CHAIN8 COMPLETE" runs/chain8_20260827.status 2>/dev/null; do
  sleep 300
done
echo "$(date '+%F %T') CHAIN9 start host=$(hostname) gpus=4,5,6,7" >> "$S"
export CUDA_VISIBLE_DEVICES=4,5,6,7
export HOLDFAST_GPUS=4,5,6,7
run() {
  echo "$(date '+%F %T') START $*" >> "$S"
  "$@"
  rc=$?
  echo "$(date '+%F %T') DONE rc=$rc $*" >> "$S"
}
run bash harness/run_dpo_cell.sh 8B 17 4
run bash harness/run_dpo_cell.sh 8B 1017 4
run bash harness/run_dpo_cell.sh 8B 2017 4
echo "$(date '+%F %T') CHAIN9 COMPLETE" >> "$S"
