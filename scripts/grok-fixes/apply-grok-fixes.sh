#!/usr/bin/env bash
# Apply / check / revert the Grok Build fixes for Trellis 0.7.0-beta.4.
#
#   apply-grok-fixes.sh [--dry-run | --revert] [--target DIR] [--only scripts|grok]
#                       [--force-version] [--no-tests] [--backup-dir DIR]
#
# Patches (scripts/grok-fixes/patches/, applied in order):
#   0001-active-task-grok-session-id.patch  .trellis/scripts/common/active_task.py
#   0002-task-store-archive-repoint.patch    .trellis/scripts/common/task_store.py
#   0003-grok-commands-aligned.patch         .grok/commands/trellis-{start,continue,finish-work}.md
#   0004-matt-flow-grok.patch                docs/agents/matt-flow.md
# 0001-0002 ("scripts") are Trellis-managed files; 0003-0004 ("grok") are this
# integration's Grok layer. 0003 is skipped when the project has no .grok/commands;
# 0004 is skipped when docs/agents/matt-flow.md is absent.
#
# Idempotent: a patch whose reverse already applies is reported "already applied"
# and left alone. A patch that does not apply cleanly (a locally customized file)
# stops the run before anything is written; customizations outside the patch
# context are kept (sha256 shows stock/patched/custom for information). Every touched file is copied to the backup dir first.
# Nothing is committed.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/platform.sh"
PATCH_DIR="$HERE/patches"
EXPECTED_VERSION="0.7.0-beta.4"
MODE=apply; TARGET=""; ONLY=all; FORCE_VERSION=0; RUN_TESTS=1; BACKUP_DIR=""

# sha256 of the Trellis 0.7.0-beta.4 stock template and of the patched file
declare -A STOCK=(
  [.trellis/scripts/common/active_task.py]=1dcba0c191bc61c49f873e7da636f7c605e0961f6abf02df2dd7cee6d122785f
  [.trellis/scripts/common/task_store.py]=73b0e07345f282986f7dfdd6760caa64d4bd6dbff41e8a624d71853260c7f828
)
declare -A PATCHED=(
  [.trellis/scripts/common/active_task.py]=dfa406b755527c2f49785853025a0d93d3b6c8385262c40e186ef448acb33337
  [.trellis/scripts/common/task_store.py]=bab9e441d9a4c50766dbfebd58c4a51a85e192745f8f267186a8e55e4d9485e8
)

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE=dry-run ;;
    --revert) MODE=revert ;;
    --target) TARGET="$2"; shift ;;
    --only) ONLY="$2"; shift ;;
    --force-version) FORCE_VERSION=1 ;;
    --no-tests) RUN_TESTS=0 ;;
    --backup-dir) BACKUP_DIR="$2"; shift ;;
    -h|--help) usage 0 ;;
    *) echo "unknown option: $1" >&2; usage 2 ;;
  esac
  shift
done

TARGET="${TARGET:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
TARGET="$(cd "$TARGET" && pwd)"
[[ -f "$TARGET/.trellis/scripts/task.py" ]] || { echo "error: $TARGET is not a Trellis project" >&2; exit 2; }
BACKUP_DIR="${BACKUP_DIR:-$HOME/trellis-backups/grok-fixes/$(basename "$TARGET")-$(date +%Y%m%d-%H%M%S)}"

version="$(tr -d ' \n\r' < "$TARGET/.trellis/.version" 2>/dev/null || echo unknown)"
echo "target:  $TARGET"
echo "trellis: $version (patches made for $EXPECTED_VERSION)"
echo "mode:    $MODE"
if [[ "$version" != "$EXPECTED_VERSION" && $FORCE_VERSION -eq 0 && "$MODE" != revert ]]; then
  echo "error: version mismatch. Re-check the patches against the new templates (see docs/grok-fixes/INSTALL.md), then rerun with --force-version." >&2
  exit 3
fi

patches=()
for p in "$PATCH_DIR"/000*.patch; do
  case "$(basename "$p")" in
    0001*|0002*) [[ "$ONLY" == all || "$ONLY" == scripts ]] && patches+=("$p") ;;
    0003*) [[ ( "$ONLY" == all || "$ONLY" == grok ) && -d "$TARGET/.grok/commands" ]] && patches+=("$p") ;;
    0004*) [[ ( "$ONLY" == all || "$ONLY" == grok ) && -f "$TARGET/docs/agents/matt-flow.md" ]] && patches+=("$p") ;;
  esac
done
[[ "$MODE" == revert ]] && { rev=(); for ((i=${#patches[@]}-1; i>=0; i--)); do rev+=("${patches[i]}"); done; patches=("${rev[@]}"); }

files_of() { grep -E '^\+\+\+ b/' "$1" | sed 's#^+++ b/##'; }
hash_state() {
  local f="$1" h
  [[ -n "${STOCK[$f]:-}" ]] || { echo "-"; return; }
  [[ -f "$TARGET/$f" ]] || { echo "missing"; return; }
  h="$(sha256sum "$TARGET/$f" | cut -d' ' -f1)"
  if [[ "$h" == "${STOCK[$f]}" ]]; then echo stock
  elif [[ "$h" == "${PATCHED[$f]}" ]]; then echo patched
  else echo "custom($h)"; fi
}
gapply() { git -C "$TARGET" apply --whitespace=nowarn "$@"; }

# Plan
todo=(); status=0
for p in "${patches[@]}"; do
  name="$(basename "$p")"; hs=""
  for f in $(files_of "$p"); do hs+=" $f:$(hash_state "$f")"; done
  if gapply --check -R "$p" 2>/dev/null; then state=applied
  elif gapply --check "$p" 2>/dev/null; then state=pending
  else state=conflict; fi
  printf '  %-42s %-9s%s\n' "$name" "$state" "$hs"
  case "$MODE:$state" in
    apply:pending|dry-run:pending|revert:applied) todo+=("$p") ;;
    apply:conflict|dry-run:conflict|revert:conflict) status=4 ;;
  esac
done
if [[ $status -ne 0 ]]; then
  echo "error: at least one patch neither applies nor is already applied (locally customized file?); nothing was changed. Merge it by hand (see docs/grok-fixes/INSTALL.md)." >&2
  exit $status
fi
if [[ "$MODE" == dry-run ]]; then
  echo "dry-run: ${#todo[@]} patch(es) would be applied; backups would go to $BACKUP_DIR"
  exit 0
fi
if [[ ${#todo[@]} -eq 0 ]]; then
  echo "nothing to do ($([[ $MODE == revert ]] && echo 'not applied' || echo 'already applied'))."
else
  mkdir -p "$BACKUP_DIR"
  for p in "${todo[@]}"; do
    for f in $(files_of "$p"); do
      [[ -f "$TARGET/$f" ]] && { mkdir -p "$BACKUP_DIR/$(dirname "$f")"; cp -p "$TARGET/$f" "$BACKUP_DIR/$f"; }
    done
    if [[ "$MODE" == revert ]]; then gapply -R "$p"; else gapply "$p"; fi
    echo "  $([[ $MODE == revert ]] && echo reverted || echo applied): $(basename "$p")"
  done
  echo "backups: $BACKUP_DIR"
fi

if [[ $RUN_TESTS -eq 1 && "$MODE" == apply && ( "$ONLY" == all || "$ONLY" == scripts ) ]]; then
  echo "--- smoke test (throwaway copy of .trellis; the target is not touched)"
  py_exec "$HERE/smoke_test.py" "$TARGET"
  if [[ -f "$TARGET/tests/test_grok_fixes.py" ]]; then
    echo "--- repo tests: ${PY[*]} -m unittest discover -s tests"
    (cd "$TARGET" && py_exec -m unittest discover -s tests 2>&1 | tail -4)
  fi
fi
