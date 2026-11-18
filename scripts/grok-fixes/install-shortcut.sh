#!/usr/bin/env bash
# Install (or uninstall) the `trellis-grok` shortcut.
#
#   scripts/grok-fixes/install-shortcut.sh [--uninstall] [--home DIR]
#
# Linux: symlink ~/.local/bin/trellis-grok -> <home>/scripts/grok-fixes/trellis-grok
# Windows: write trellis-grok.cmd and trellis-grok.ps1 into a user-writable
# directory already on PATH, or %USERPROFILE%\.local\bin. No Administrator
# and no symlink. The .cmd launcher uses Git for Windows bash.exe, never
# C:\Windows\System32\bash.exe.
#
# XDG_BIN_HOME overrides the destination directory on every platform.
# Backs up an existing non-symlink file before overwriting on Linux.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/platform.sh"
HOME_SRC="$(cd "$HERE/../.." && pwd)"
MODE=install

while [[ $# -gt 0 ]]; do
  case "$1" in
    --uninstall) MODE=uninstall ;;
    --home)
      [[ $# -ge 2 ]] || { echo "error: --home needs a directory" >&2; exit 2; }
      HOME_SRC="$(normalize_path "$2")"
      HOME_SRC="$(cd "$HOME_SRC" && pwd)"
      shift
      ;;
    -h|--help)
      sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

SRC="$HOME_SRC/scripts/grok-fixes/trellis-grok"
[[ -f "$SRC" ]] || { echo "error: missing $SRC" >&2; exit 2; }
if ! is_windows; then
  [[ -x "$SRC" ]] || { echo "error: missing executable $SRC" >&2; exit 2; }
fi

shortcut_dir() {
  if [[ -n "${XDG_BIN_HOME:-}" ]]; then
    normalize_path "$XDG_BIN_HOME"
    return 0
  fi
  if is_windows; then
    windows_shortcut_dir
    return 0
  fi
  printf '%s\n' "$HOME/.local/bin"
}

note_if_missing_from_path() {
  local dir="$1"
  if path_contains_dir "$dir"; then
    return 0
  fi
  local shown="$dir"
  if is_windows; then
    shown="$(to_windows_path "$dir")"
  fi
  echo "note: $shown is not on PATH. Add it to your user PATH, then open a new terminal."
}

write_crlf() {
  local dest="$1"
  sed 's/\r$//' | sed 's/$/\r/' > "$dest"
}

install_windows() {
  local dir cmd ps1 invoke src_win invoke_win
  dir="$(shortcut_dir)"
  mkdir -p "$dir"
  cmd="$dir/trellis-grok.cmd"
  ps1="$dir/trellis-grok.ps1"
  invoke="$HOME_SRC/scripts/grok-fixes/invoke-git-bash.cmd"
  [[ -f "$invoke" ]] || { echo "error: missing $invoke" >&2; exit 2; }
  src_win="$(to_windows_path "$SRC")"
  invoke_win="$(to_windows_path "$invoke")"
  write_crlf "$cmd" <<EOF
@echo off
call "$invoke_win" "$src_win" %*
exit /b %ERRORLEVEL%
EOF
  write_crlf "$ps1" <<EOF
# Installed trellis-grok shortcut. Calls the checkout's Git Bash launcher.
\$ErrorActionPreference = "Stop"
& "$invoke_win" "$src_win" @args
exit \$LASTEXITCODE
EOF
  echo "installed: $cmd"
  echo "installed: $ps1"
  echo "source: $src_win"
  note_if_missing_from_path "$dir"
}

uninstall_windows() {
  local dir removed=0 f
  dir="$(shortcut_dir)"
  for f in "$dir/trellis-grok.cmd" "$dir/trellis-grok.ps1"; do
    if [[ -f "$f" ]]; then
      rm -f "$f"
      echo "removed: $f"
      removed=1
    fi
  done
  if [[ $removed -eq 0 ]]; then
    echo "nothing to remove ($dir/trellis-grok.cmd not present)"
  fi
}

install_unix() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ -L "$dest" ]]; then
      local cur
      cur="$(readlink "$dest")"
      if [[ "$cur" == "$SRC" ]]; then
        echo "already installed: $dest -> $SRC"
        note_if_missing_from_path "$(dirname "$dest")"
        return 0
      fi
      echo "replacing symlink $dest (-> $cur)"
      rm -f "$dest"
    else
      local bak="$dest.bak.$(date +%Y%m%d-%H%M%S)"
      cp -p "$dest" "$bak"
      echo "backed up existing file to $bak"
      rm -f "$dest"
    fi
  fi
  ln -s "$SRC" "$dest"
  echo "installed: $dest -> $SRC"
  note_if_missing_from_path "$(dirname "$dest")"
}

uninstall_unix() {
  local dest="$1"
  if [[ -L "$dest" || -f "$dest" ]]; then
    rm -f "$dest"
    echo "removed: $dest"
  else
    echo "nothing to remove ($dest not present)"
  fi
}

if is_windows; then
  if [[ "$MODE" == uninstall ]]; then
    uninstall_windows
  else
    install_windows
  fi
  exit 0
fi

DEST="$(shortcut_dir)/trellis-grok"
if [[ "$MODE" == uninstall ]]; then
  uninstall_unix "$DEST"
else
  install_unix "$DEST"
fi
