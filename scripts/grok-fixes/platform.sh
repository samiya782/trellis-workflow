# Shared platform helpers for trellis-matt, oneclick.sh, install-shortcut.sh,
# and apply-grok-fixes.sh. Source this file; do not execute it for install.
#
# Windows clone cache: %LOCALAPPDATA%\trellis-matt\workflow
# Linux clone cache: $XDG_CACHE_HOME/trellis-matt/workflow or ~/.cache/trellis-matt/workflow
# Override either with TRELLIS_MATT_CLONE_DIR.
# TRELLIS_MATT_PLATFORM=windows|unix forces detection (tests). Real Windows
# Git Bash is detected from uname (MINGW/MSYS/CYGWIN).

platform_kind() {
  if [[ -n "${TRELLIS_MATT_PLATFORM:-}" ]]; then
    case "${TRELLIS_MATT_PLATFORM}" in
      windows|win) printf '%s\n' windows ;;
      unix|linux|mac) printf '%s\n' unix ;;
      *) printf '%s\n' "${TRELLIS_MATT_PLATFORM}" ;;
    esac
    return 0
  fi
  case "$(uname -s 2>/dev/null || echo unknown)" in
    MINGW*|MSYS*|CYGWIN*) printf '%s\n' windows ;;
    *) printf '%s\n' unix ;;
  esac
}

is_windows() {
  [[ "$(platform_kind)" == "windows" ]]
}

# Turn a Windows path into the form the current shell can cd to.
# Git Bash cygpath converts "C:\..." ; Linux leaves the string alone.
normalize_path() {
  local p="$1"
  if [[ -z "$p" ]]; then
    printf '%s\n' ""
    return 0
  fi
  if is_windows && command -v cygpath >/dev/null 2>&1; then
    case "$p" in
      [A-Za-z]:*|*[\\]*)
        cygpath -u "$p"
        return 0
        ;;
    esac
  fi
  printf '%s\n' "$p"
}

# Native path for files a Windows user will open (cmd/PowerShell).
to_windows_path() {
  local p="$1"
  if command -v cygpath >/dev/null 2>&1 && is_windows; then
    cygpath -w "$p"
    return 0
  fi
  printf '%s\n' "$p"
}

default_clone_dir() {
  if [[ -n "${TRELLIS_MATT_CLONE_DIR:-}" ]]; then
    normalize_path "$TRELLIS_MATT_CLONE_DIR"
    return 0
  fi
  if is_windows; then
    local base="${LOCALAPPDATA:-}"
    if [[ -z "$base" ]]; then
      base="${USERPROFILE:-$HOME}/AppData/Local"
    fi
    base="$(normalize_path "$base")"
    printf '%s\n' "${base%/}/trellis-matt/workflow"
    return 0
  fi
  printf '%s\n' "${XDG_CACHE_HOME:-$HOME/.cache}/trellis-matt/workflow"
}

python_is_3() {
  "$@" -c 'import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)' >/dev/null 2>&1
}

# Sets the global PY array to (python3), (python), or (py -3).
# TRELLIS_MATT_PYTHON, when set, is split and used as-is.
resolve_python() {
  if [[ -n "${TRELLIS_MATT_PYTHON:-}" ]]; then
    # shellcheck disable=SC2206
    PY=(${TRELLIS_MATT_PYTHON})
    return 0
  fi
  if command -v python3 >/dev/null 2>&1 && python_is_3 python3; then
    PY=(python3)
    return 0
  fi
  if command -v python >/dev/null 2>&1 && python_is_3 python; then
    PY=(python)
    return 0
  fi
  if command -v py >/dev/null 2>&1 && python_is_3 py -3; then
    PY=(py -3)
    return 0
  fi
  echo "error: Python 3 not found (tried python3, python, py -3)" >&2
  return 2
}

py_exec() {
  if [[ -z "${PY+x}" || ${#PY[@]} -eq 0 ]]; then
    resolve_python || return $?
  fi
  "${PY[@]}" "$@"
}

fold_path() {
  printf '%s' "${1%/}" | tr '[:upper:]' '[:lower:]'
}

path_contains_dir() {
  local dir want part flat
  dir="${1%/}"
  want="$(fold_path "$dir")"
  flat="${PATH//;/:}"
  local IFS=:
  for part in $flat; do
    part="${part%/}"
    [[ -z "$part" ]] && continue
    if [[ "$(fold_path "$part")" == "$want" ]]; then
      return 0
    fi
  done
  return 1
}

# Package-manager trees and system directories are a bad place for a user shim.
skip_shortcut_dir() {
  local low
  low="$(fold_path "$1")"
  case "$low" in
    *"/mise/installs/"*|*"\\mise\\installs\\"*) return 0 ;;
    *"/node_modules/"*|*"\\node_modules\\"*) return 0 ;;
    *"/windowsapps"*|*"\\windowsapps"*) return 0 ;;
    *"/windows"*|*"\\windows"*) return 0 ;;
    *"/program files"*|*"\\program files"*) return 0 ;;
  esac
  return 1
}

under_user_profile() {
  local part profile
  part="$(fold_path "$1")"
  profile="$(fold_path "$2")"
  [[ -n "$profile" && ( "$part" == "$profile" || "$part" == "$profile"/* ) ]]
}

# Directory that should receive trellis-matt.cmd. Caller still prints a PATH note.
windows_shortcut_dir() {
  local home profile preferred
  home="$(normalize_path "${USERPROFILE:-$HOME}")"
  home="${home%/}"
  profile="$home"
  local -a preferred_dirs=(
    "$home/.local/bin"
    "$home/bin"
  )
  if [[ -n "${APPDATA:-}" ]]; then
    preferred_dirs+=("$(normalize_path "$APPDATA")/npm")
  fi
  for preferred in "${preferred_dirs[@]}"; do
    preferred="${preferred%/}"
    if path_contains_dir "$preferred"; then
      printf '%s\n' "$preferred"
      return 0
    fi
  done
  local part flat
  flat="${PATH//;/:}"
  local IFS=:
  for part in $flat; do
    part="${part%/}"
    [[ -z "$part" || ! -d "$part" || ! -w "$part" ]] && continue
    skip_shortcut_dir "$part" && continue
    if under_user_profile "$part" "$profile"; then
      printf '%s\n' "$part"
      return 0
    fi
  done
  printf '%s\n' "$home/.local/bin"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  case "${1:-}" in
    kind) platform_kind ;;
    clone-dir) default_clone_dir ;;
    python)
      resolve_python || exit $?
      printf '%s\n' "${PY[*]}"
      ;;
    shortcut-dir) windows_shortcut_dir ;;
    *)
      echo "usage: platform.sh {kind|clone-dir|python|shortcut-dir}" >&2
      exit 2
      ;;
  esac
fi
