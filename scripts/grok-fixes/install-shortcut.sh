#!/usr/bin/env bash
# Install (or uninstall) the `trellis-grok` shortcut into ~/.local/bin.
#
#   scripts/grok-fixes/install-shortcut.sh [--uninstall] [--home DIR]
#
# Creates a symlink ~/.local/bin/trellis-grok -> <home>/scripts/grok-fixes/trellis-grok
# Backs up an existing non-symlink file before overwriting.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_SRC="$(cd "$HERE/../.." && pwd)"
DEST="${XDG_BIN_HOME:-$HOME/.local/bin}/trellis-grok"
MODE=install

while [[ $# -gt 0 ]]; do
  case "$1" in
    --uninstall) MODE=uninstall ;;
    --home) HOME_SRC="$(cd "$2" && pwd)"; shift ;;
    -h|--help)
      sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

SRC="$HOME_SRC/scripts/grok-fixes/trellis-grok"
[[ -x "$SRC" ]] || { echo "error: missing executable $SRC" >&2; exit 2; }

if [[ "$MODE" == uninstall ]]; then
  if [[ -L "$DEST" || -f "$DEST" ]]; then
    rm -f "$DEST"
    echo "removed: $DEST"
  else
    echo "nothing to remove ($DEST not present)"
  fi
  exit 0
fi

mkdir -p "$(dirname "$DEST")"
if [[ -e "$DEST" || -L "$DEST" ]]; then
  if [[ -L "$DEST" ]]; then
    cur="$(readlink "$DEST")"
    if [[ "$cur" == "$SRC" ]]; then
      echo "already installed: $DEST -> $SRC"
      exit 0
    fi
    echo "replacing symlink $DEST (-> $cur)"
    rm -f "$DEST"
  else
    bak="$DEST.bak.$(date +%Y%m%d-%H%M%S)"
    cp -p "$DEST" "$bak"
    echo "backed up existing file to $bak"
    rm -f "$DEST"
  fi
fi

ln -s "$SRC" "$DEST"
echo "installed: $DEST -> $SRC"
case ":$PATH:" in
  *":$(dirname "$DEST"):"*) ;;
  *) echo "note: $(dirname "$DEST") is not on PATH; add it or open a new shell" ;;
esac
