#!/usr/bin/env bash
# One-click Trellis + Matt setup for Claude Code, Codex, and Grok Build.
#
# From this checkout, or from a clone of branch grok:
#   scripts/grok-fixes/oneclick.sh [DIR] [-u NAME] [--claude] [--codex] [--grok]
#
# Flags are the same as `trellis-grok install`, including --from-github and
# --no-skills. No platform flags installs all three.
#
# A downloaded copy of this file (no neighboring trellis-grok) clones
# https://github.com/samiya782/trellis-workflow branch grok, then runs that
# clone's `trellis-grok install`. Cache: TRELLIS_GROK_CLONE_DIR, or
# $XDG_CACHE_HOME/trellis-grok/workflow, or ~/.cache/trellis-grok/workflow.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$HERE/trellis-grok" ]]; then
  exec "$HERE/trellis-grok" install "$@"
fi

repo="${TRELLIS_GROK_REPO:-https://github.com/samiya782/trellis-workflow.git}"
branch="${TRELLIS_GROK_BRANCH:-grok}"
dest="${TRELLIS_GROK_CLONE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/trellis-grok/workflow}"
if [[ ! -x "$dest/scripts/grok-fixes/trellis-grok" ]]; then
  if [[ -e "$dest" ]]; then
    echo "error: $dest exists but has no scripts/grok-fixes/trellis-grok" >&2
    exit 2
  fi
  mkdir -p "$(dirname "$dest")"
  echo "--- clone $repo branch $branch -> $dest" >&2
  git clone --depth 1 --branch "$branch" "$repo" "$dest"
fi
exec "$dest/scripts/grok-fixes/trellis-grok" install "$@"
