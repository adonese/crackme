#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v wine >/dev/null 2>&1; then
  cat >&2 <<'MSG'
Wine is not installed or not on PATH.

Install Wine, then rerun this launcher.
MSG
  exit 1
fi

choose_binary() {
  local -a files=()
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(
    find "$ROOT/crackmes" "$ROOT/practice" -type f \
      \( -iname '*.exe' -o -iname '*.scr' \) -print0 | sort -z
  )

  if [[ "${#files[@]}" -eq 0 ]]; then
    echo "No .exe or .scr files found under crackmes/ or practice/." >&2
    return 1
  fi

  if command -v fzf >/dev/null 2>&1; then
    printf '%s\n' "${files[@]}" | sed "s#^$ROOT/##" | fzf --prompt='wine> '
    return
  fi

  local i
  for i in "${!files[@]}"; do
    printf '%3d) %s\n' "$((i + 1))" "${files[$i]#$ROOT/}" >&2
  done

  local choice
  printf 'Select binary: ' >&2
  read -r choice
  if ! [[ "$choice" =~ ^[0-9]+$ ]] || (( choice < 1 || choice > ${#files[@]} )); then
    echo "Invalid selection." >&2
    return 1
  fi

  printf '%s\n' "${files[$((choice - 1))]#$ROOT/}"
}

target="${1:-}"
if [[ -z "$target" ]]; then
  target="$(choose_binary)"
fi

case "$target" in
  /*) full_path="$target" ;;
  *) full_path="$ROOT/$target" ;;
esac

if [[ ! -f "$full_path" ]]; then
  echo "Not a file: $target" >&2
  exit 1
fi

: "${WINEPREFIX:=$ROOT/.wine-prefix}"
export WINEPREFIX

cd "$(dirname "$full_path")"
exec wine "$(basename "$full_path")"
