#!/usr/bin/env bash
# launch interactive grok TUI for run $1 with session id $2 in tmux session $1
set -euo pipefail
r=$1; sid=$2; B=$HOME/tmp/trellis-grok-val-20261026; R=/tmp/grokval/hs/runs/$r
tmux kill-session -t "$r" 2>/dev/null || true
tmux new-session -d -s "$r" -x 200 -y 50 -c "$B/$r"
tmux pipe-pane -t "$r" -o "cat >> $R/raw-pipe.log"
echo "$sid" > $R/session-id.txt
echo "$(date -Iseconds) launch sid=$sid" >> $R/interactions.log
tmux send-keys -t "$r" "grok -s $sid -m grok-4.7-build-fast --always-approve --deny 'Bash(git commit:*)' --deny 'Bash(git push:*)' --deny 'Bash(git reset:*)' --deny 'Bash(git checkout:*)' --deny 'Bash(git stash:*)' --deny 'Bash(rm -rf:*)'" Enter
