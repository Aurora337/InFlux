#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [ -f "mkdocs.yml" ]; then
  if ! command -v mkdocs >/dev/null 2>&1; then
    echo "mkdocs not found. Install with: pip install mkdocs"
    exit 2
  fi
  echo "Building MkDocs site..."
  mkdocs build
  exit 0
fi

if [ -d "docs" ]; then
  if [ -f "docs/conf.py" ] || [ -d "docs/_templates" ]; then
    if ! command -v sphinx-build >/dev/null 2>&1; then
      echo "sphinx-build not found. Install with: pip install sphinx"
      exit 2
    fi
    echo "Building Sphinx docs..."
    sphinx-build -b html docs docs/_build/html
    exit 0
  fi
fi

echo "No supported docs configuration found (mkdocs.yml or Sphinx docs)."
exit 1
