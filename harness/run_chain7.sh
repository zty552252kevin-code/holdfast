#!/bin/bash
# chain7: s17 make-up runs + 14B salvage evals (see DECISIONS D-021/D-022).
#   1. DPO 8B s17     — re-run under the fixed train_dpo.py (device fix, D-021)
#   2. 14B 4k s17     — full run; first exercise of the device-robust D-016
#                       verify (train_sft.py fix, D-022)
#   3. 14B 4k s1017/2017 — final/ already saved & intact; run_cell.sh skips
#                       training and runs gen_check + eval only (salvage)
# rc discipline: capture rc=$? BEFORE the echo (the chain5/6 rc trap).
cd /data/holdfast
S=runs/chain7_20260826.status
echo "$(date '+%F %T') CHAIN7 start host=$(hostname) gpus=4,5,6,7" >> "$S"
export CUDA_VISIBLE_DEVICES=4,5,6,7
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
echo "$(date '+%F %T') CHAIN7 COMPLETE" >> "$S"
