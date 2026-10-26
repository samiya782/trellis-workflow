#!/usr/bin/env bash
# type message $2 (key M1/M2/MQ) into run $1 as the human proxy
set -euo pipefail
r=$1; key=$2; R=/tmp/grokval/hs/runs/$r
case $key in
  M1) msg='/trellis-continue .trellis/tasks/10-26-textstats-top';;
  M2) msg='The PRD is approved as complete. You are authorized to implement this task now. Do not commit and do not push.';;
  M3) msg='/implement .trellis/tasks/10-26-textstats-top';;
  MQ) msg='Use your recommended option and continue. Do not commit and do not push.';;
  *) echo bad key; exit 2;;
esac
tmux send-keys -t "$r" -l "$msg"; sleep 1.5; tmux send-keys -t "$r" Enter
echo "$(date -Iseconds) [$key] typed (answered by assistant on behalf of user): $msg" >> $R/interactions.log
