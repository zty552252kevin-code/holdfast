#!/bin/bash
# chain8: DPO-8B-s17 eval re-run (D-023) + 14B retrain under the DCP save
# path (D-024). Broken 14B finals deleted before launch (layer-25 holes).
cd /data/holdfast
S=runs/chain8_20260827.status
echo "$(date '+%F %T') CHAIN8 start host=$(hostname) gpus=4,5,6,7" >> "$S"
export CUDA_VISIBLE_DEVICES=4,5,6,7
export HOLDFAST_GPUS=4,5,6,7
run() {
  echo "$(date '+%F %T') START $*" >> "$S"
  "$@"
  rc=$?
  echo "$(date '+%F %T') DONE rc=$rc $*" >> "$S"
}
run bash harness/run_dpo_cell.sh 8B 17 4
run bash harness/run_cell.sh 14B 4k 17 4
run bash harness/run_cell.sh 14B 4k 1017 4
run bash harness/run_cell.sh 14B 4k 2017 4
echo "$(date '+%F %T') CHAIN8 COMPLETE" >> "$S"
