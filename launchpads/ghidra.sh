#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CALLER_PWD="$PWD"

usage() {
  cat <<'USAGE'
Usage:
  ./launchpad ghidra [file.exe]
  ./launchpad ghidra [project.gpr]
  ./launchpad ghidra [--import-only] [--reimport] [--no-analysis] [file.exe]

Options:
  --import-only        Import/analyze the file, then stop before launching GUI
  --reimport           Re-import even if the per-file project already exists
  --no-analysis        Import without auto-analysis
  --project NAME       Use a specific project name instead of auto-naming
  --project-dir DIR    Store projects in DIR instead of ~/ghidra-projects/quick

Environment:
  GHIDRA_HOME          Directory containing ghidraRun
  GHIDRA_PROJECT_DIR   Default project directory for quick imports
USAGE
}

find_ghidra_run() {
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
    "$HOME"/tools/ghidra*/ghidraRun \
    "$HOME"/src/ghidra/ghidra*/ghidraRun; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

resolve_path() {
  local raw="$1"
  if command -v wslpath >/dev/null 2>&1 && [[ "$raw" =~ ^[A-Za-z]:\\ ]]; then
    raw="$(wslpath -u "$raw")"
  fi
  if [[ "$raw" != /* ]]; then
    raw="$CALLER_PWD/$raw"
  fi
  if command -v realpath >/dev/null 2>&1; then
    realpath "$raw"
  else
    (cd "$(dirname "$raw")" && printf '%s/%s\n' "$PWD" "$(basename "$raw")")
  fi
}

resolve_new_path() {
  local raw="$1"
  if command -v wslpath >/dev/null 2>&1 && [[ "$raw" =~ ^[A-Za-z]:\\ ]]; then
    raw="$(wslpath -u "$raw")"
  fi
  if [[ "$raw" != /* ]]; then
    raw="$CALLER_PWD/$raw"
  fi
  if command -v realpath >/dev/null 2>&1; then
    realpath -m "$raw"
  else
    (mkdir -p "$(dirname "$raw")" && cd "$(dirname "$raw")" && printf '%s/%s\n' "$PWD" "$(basename "$raw")")
  fi
}

sanitize_name() {
  local value="$1"
  value="${value%.*}"
  value="$(printf '%s' "$value" | tr -c 'A-Za-z0-9._-' '_' | sed -E 's/_+/_/g; s/^_//; s/_$//')"
  printf '%s\n' "${value:-program}"
}

project_name_for() {
  local target="$1"
  local base hash
  base="$(sanitize_name "$(basename "$target")")"
  hash="$(printf '%s' "$target" | sha256sum | awk '{print substr($1, 1, 10)}')"
  printf '%s-%s\n' "$base" "$hash"
}

ghidra_run="$(find_ghidra_run || true)"
if [[ -z "$ghidra_run" ]]; then
  cat >&2 <<'MSG'
Could not find ghidraRun.

Install Ghidra, then either:
  export GHIDRA_HOME=/path/to/ghidra
or put ghidraRun on PATH.
MSG
  exit 1
fi

ghidra_home="$(cd "$(dirname "$ghidra_run")" && pwd)"
analyze_headless="$ghidra_home/support/analyzeHeadless"

import_only=0
reimport=0
analysis=1
project_name=""
project_dir="${GHIDRA_PROJECT_DIR:-$HOME/ghidra-projects/quick}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --import-only)
      import_only=1
      shift
      ;;
    --reimport)
      reimport=1
      shift
      ;;
    --no-analysis)
      analysis=0
      shift
      ;;
    --project)
      project_name="${2:-}"
      if [[ -z "$project_name" ]]; then
        echo "--project requires a name" >&2
        exit 2
      fi
      shift 2
      ;;
    --project-dir)
      project_dir="${2:-}"
      if [[ -z "$project_dir" ]]; then
        echo "--project-dir requires a directory" >&2
        exit 2
      fi
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  cd "$ROOT"
  exec "$ghidra_run"
fi

if [[ $# -ne 1 ]]; then
  cd "$ROOT"
  exec "$ghidra_run" "$@"
fi

target="$(resolve_path "$1")"
if [[ ! -f "$target" ]]; then
  echo "Not a file: $1" >&2
  exit 2
fi

if [[ "$target" == *.gpr ]]; then
  exec "$ghidra_run" "$target"
fi

if [[ ! -r "$analyze_headless" ]]; then
  cat >&2 <<MSG
Could not find readable analyzeHeadless at:
  $analyze_headless

Raw files need analyzeHeadless so they can be imported before Ghidra opens.
MSG
  exit 1
fi

project_dir="$(resolve_new_path "$project_dir")"
project_name="${project_name:-$(project_name_for "$target")}"
project_file="$project_dir/$project_name.gpr"
mkdir -p "$project_dir"

if [[ ! -f "$project_file" || "$reimport" -eq 1 ]]; then
  args=("$project_dir" "$project_name" -import "$target" -overwrite)
  if [[ "$analysis" -eq 0 ]]; then
    args+=(-noanalysis)
  fi
  echo "[ghidra] importing $target"
  echo "[ghidra] project   $project_file"
  if ! bash "$analyze_headless" "${args[@]}"; then
    if [[ -f "$project_file" ]]; then
      echo "[ghidra] import failed; opening existing project anyway" >&2
    else
      exit 1
    fi
  fi
else
  echo "[ghidra] opening existing project $project_file"
  echo "[ghidra] use --reimport to refresh it from $target"
fi

if [[ "$import_only" -eq 1 ]]; then
  echo "$project_file"
  exit 0
fi

exec "$ghidra_run" "$project_file"
