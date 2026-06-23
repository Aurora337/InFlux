#!/usr/bin/env bash
set -e

echo "🧱 Installing package..."
pip install -e .

echo "🧪 Running tests..."
pytest -q

echo "🚀 Running CLI smoke test..."
python -m influx.cli
