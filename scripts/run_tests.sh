#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Activate venv if present
if [ -d ".venv" ]; then
  # shellcheck disable=SC1090
  . .venv/bin/activate
fi

PYTHON_CMD=""
if command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
else
  echo "No Python executable found in PATH (python/python3)."
  exit 2
fi

echo "Running pytest..."
"$PYTHON_CMD" -m pytest -q
