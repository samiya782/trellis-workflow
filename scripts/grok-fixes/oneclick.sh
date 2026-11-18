#!/usr/bin/env bash
# One-click Trellis + Matt setup for Claude Code, Codex, and Grok Build.
# Opt-in clients, not part of the no-flag default: --codefree-o and
# --codefree-space (CodeFree Space). Official trellis init has no flag for
# those clients; trellis-matt install writes the files they load.
#
# From this checkout, or from a clone of branch main:
#   scripts/grok-fixes/oneclick.sh [DIR] [-u NAME] [--claude] [--codex] [--grok]
#       [--codefree-o] [--codefree-space]
#
# Flags are the same as `trellis-matt install`, including --from-github and
# --no-skills, and are forwarded with "$@". No platform flags installs
# Claude Code, Codex, and Grok Build.
#
# A downloaded copy of this file (no neighboring trellis-matt) clones
# https://github.com/samiya782/trellis-workflow branch main, then runs that
# clone's `trellis-matt install`. Cache: TRELLIS_MATT_CLONE_DIR, or
# $XDG_CACHE_HOME/trellis-matt/workflow, or ~/.cache/trellis-matt/workflow
# on Linux. On Windows the default is %LOCALAPPDATA%\trellis-matt\workflow.
# Windows users run oneclick.cmd or oneclick.ps1 so Git for Windows bash.exe
# is used. curl | bash is a Linux (or Git Bash) form; it does not run in cmd.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$HERE/trellis-matt" ]]; then
  exec "$HERE/trellis-matt" install "$@"
fi

# Keep this fallback in sync with scripts/grok-fixes/platform.sh. A curl|bash
# download has no neighboring platform.sh, so the default cache dir is inlined.
default_clone_dir() {
  if [[ -n "${TRELLIS_MATT_CLONE_DIR:-}" ]]; then
    local override="$TRELLIS_MATT_CLONE_DIR"
    case "$(uname -s 2>/dev/null || echo unknown)" in
      MINGW*|MSYS*|CYGWIN*)
        if command -v cygpath >/dev/null 2>&1; then
          case "$override" in
            [A-Za-z]:*|*[\\]*) override="$(cygpath -u "$override")" ;;
          esac
        fi
        ;;
    esac
    printf '%s\n' "$override"
    return 0
  fi
  case "$(uname -s 2>/dev/null || echo unknown)" in
    MINGW*|MSYS*|CYGWIN*)
      local base="${LOCALAPPDATA:-${USERPROFILE:-$HOME}/AppData/Local}"
      if command -v cygpath >/dev/null 2>&1; then
        case "$base" in
          [A-Za-z]:*|*[\\]*) base="$(cygpath -u "$base")" ;;
        esac
      fi
      printf '%s\n' "${base%/}/trellis-matt/workflow"
      ;;
    *)
      printf '%s\n' "${XDG_CACHE_HOME:-$HOME/.cache}/trellis-matt/workflow"
      ;;
  esac
}

repo="${TRELLIS_MATT_REPO:-https://github.com/samiya782/trellis-workflow.git}"
branch="${TRELLIS_MATT_BRANCH:-main}"
dest="$(default_clone_dir)"
export GIT_TERMINAL_PROMPT=0
if [[ ! -x "$dest/scripts/grok-fixes/trellis-matt" ]]; then
  if [[ -e "$dest" ]]; then
    echo "error: $dest exists but has no scripts/grok-fixes/trellis-matt" >&2
    exit 2
  fi
  mkdir -p "$(dirname "$dest")"
  echo "--- clone $repo branch $branch -> $dest" >&2
  git clone --depth 1 --branch "$branch" "$repo" "$dest"
fi
exec "$dest/scripts/grok-fixes/trellis-matt" install "$@"
