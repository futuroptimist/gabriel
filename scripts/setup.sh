#!/usr/bin/env bash

# Bootstrap the Gabriel development environment.
#
# The script creates a Python virtual environment, installs project dependencies,
# and sets up pre-commit hooks. Pass --dry-run to preview the actions without
# executing them.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/setup.sh [--dry-run] [--python PYTHON]

Options:
  --dry-run      Print the commands that would be executed without running them.
  --python BIN   Explicit python interpreter to use.
                 Defaults to python3 and falls back to python when unavailable.
  -h, --help     Show this help message and exit.
USAGE
}

DRY_RUN=0
PYTHON_BIN="${PYTHON_BIN:-python3}"

while (($# > 0)); do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --python)
      if (($# < 2)); then
        echo "error: --python requires an interpreter name" >&2
        usage
        exit 1
      fi
      PYTHON_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option '$1'" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  if [[ "$PYTHON_BIN" == "python3" ]] && command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "error: python interpreter not found: $PYTHON_BIN" >&2
    exit 1
  fi
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$REPO_ROOT/.venv"
VENV_PYTHON="$VENV_PATH/bin/python"

log() {
  printf '%s\n' "$1"
}

run_cmd() {
  if (($DRY_RUN)); then
    printf '[dry-run] %s\n' "$*"
  else
    printf '+ %s\n' "$*"
    "$@"
  fi
}

if [[ ! -d "$VENV_PATH" ]]; then
  log "Creating virtual environment at $VENV_PATH"
  run_cmd "$PYTHON_BIN" -m venv "$VENV_PATH"
else
  log "Virtual environment already exists at $VENV_PATH"
fi

run_cmd "$VENV_PYTHON" -m pip install --upgrade pip
run_cmd "$VENV_PYTHON" -m pip install -r "$REPO_ROOT/requirements.txt"
run_cmd "$VENV_PYTHON" -m pip install pre-commit
run_cmd "$VENV_PYTHON" -m pre-commit install

log "Bootstrap complete. Activate the environment with: source $VENV_PATH/bin/activate"
