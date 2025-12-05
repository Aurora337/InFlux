#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Ensure harness directory is on PYTHONPATH
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

python3 - <<'PY'
from harness.replay_engine import ReplayEngine
engine = ReplayEngine(events=[{"example": 1}, {"example": 2}])
out = engine.replay()
print("Replayed events:", out)
PY
