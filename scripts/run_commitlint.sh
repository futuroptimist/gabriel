#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/run_commitlint.sh [commit-message-file]

When executed as part of a pre-commit hook the commit message file is provided
via the PRE_COMMIT_COMMIT_MSG_FILENAME environment variable.
USAGE
}

TARGET="${1:-${PRE_COMMIT_COMMIT_MSG_FILENAME:-}}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ -z "${TARGET}" ]]; then
  echo "error: commit message file not provided" >&2
  usage
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx is required to run commitlint" >&2
  exit 1
fi

npx commitlint --edit "${TARGET}"
