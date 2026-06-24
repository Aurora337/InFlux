#!/usr/bin/env bash
set -e

PYTHON_CMD=""
if command -v python >/dev/null 2>&1; then
	PYTHON_CMD="python"
elif command -v python3 >/dev/null 2>&1; then
	PYTHON_CMD="python3"
else
	echo "No Python executable found in PATH (python/python3)."
	exit 2
fi

echo "🧱 Installing package..."
"$PYTHON_CMD" -m pip install -e .

echo "🧪 Running tests..."
"$PYTHON_CMD" -m pytest -q

echo "🚀 Running CLI smoke test..."
"$PYTHON_CMD" -m influx.cli
