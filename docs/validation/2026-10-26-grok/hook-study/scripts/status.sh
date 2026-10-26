#!/usr/bin/env bash
# print busy/idle per run plus last lines
for r in "$@"; do
  c=$(tmux capture-pane -p -t "$r" 2>/dev/null)
  if echo "$c" | grep -q '\[stop\]'; then s=BUSY; else s=IDLE; fi
  echo "=== $r $s"
  echo "$c" | grep -v '^\s*█\?\s*$' | tail -${N:-12}
done
