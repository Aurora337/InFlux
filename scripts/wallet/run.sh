#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1090
  . .venv/bin/activate
fi

PYTHONPATH="$REPO_ROOT/src" python -m influx.wallet.cli "$@"
