#!/usr/bin/env bash
# wrap every .claude/hooks/*.py and .codex/hooks/*.py of fixture $1 with the trace wrapper
set -euo pipefail
F=$1
for d in "$F/.claude/hooks" "$F/.codex/hooks"; do
  [ -d "$d" ] || continue
  for h in "$d"/*.py; do
    case "$h" in *.orig.py) continue;; esac
    [ -f "${h%.py}.orig.py" ] && continue
    mv "$h" "${h%.py}.orig.py"
    cp /tmp/grokval/hs/trace_wrapper.py "$h"
  done
done
ls "$F/.claude/hooks" "$F/.codex/hooks" 2>/dev/null
