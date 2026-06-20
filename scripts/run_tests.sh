#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Activate venv if present
if [ -d ".venv" ]; then
  # shellcheck disable=SC1090
  . .venv/bin/activate
fi

echo "Running pytest..."
if command -v pytest >/dev/null 2>&1; then
  pytest -q
else
  echo "pytest not found. Install with: pip install pytest"
  exit 2
fi
