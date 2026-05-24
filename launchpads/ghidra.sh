#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find_ghidra() {
  if [[ -n "${GHIDRA_HOME:-}" && -x "$GHIDRA_HOME/ghidraRun" ]]; then
    printf '%s\n' "$GHIDRA_HOME/ghidraRun"
    return 0
  fi

  if command -v ghidraRun >/dev/null 2>&1; then
    command -v ghidraRun
    return 0
  fi

  local candidate
  for candidate in \
    /opt/ghidra*/ghidraRun \
    /usr/local/ghidra*/ghidraRun \
    "$HOME"/ghidra*/ghidraRun \
    "$HOME"/tools/ghidra*/ghidraRun; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

ghidra_run="$(find_ghidra || true)"
if [[ -z "$ghidra_run" ]]; then
  cat >&2 <<'MSG'
Could not find ghidraRun.

Install Ghidra, then either:
  export GHIDRA_HOME=/path/to/ghidra
or put ghidraRun on PATH.
MSG
  exit 1
fi

cd "$ROOT"
exec "$ghidra_run" "$@"
