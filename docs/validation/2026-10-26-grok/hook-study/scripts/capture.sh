#!/usr/bin/env bash
# save full tmux scrollback + final screen for each run, then kill the session
for r in "$@"; do R=/tmp/grokval/hs/runs/$r
  tmux capture-pane -p -J -S - -t "$r" > $R/tmux-scrollback.txt 2>/dev/null
  tmux capture-pane -p -t "$r" > $R/tmux-final-screen.txt 2>/dev/null
  echo "$(date -Iseconds) captured; session killed" >> $R/interactions.log
  tmux kill-session -t "$r" 2>/dev/null; echo "$r $(wc -l < $R/tmux-scrollback.txt) lines"
done
