#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd ""){dirname "$0"}/.." && pwd)"

echo "Setting up development environment in $REPO_ROOT"

# Python venv
if [ ! -d "$REPO_ROOT/.venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv "$REPO_ROOT/.venv"
fi

# Activate
# shellcheck disable=SC1090
. "$REPO_ROOT/.venv/bin/activate"

# Install requirements if present
if [ -f "$REPO_ROOT/requirements.txt" ]; then
  echo "Installing Python requirements..."
  pip install --upgrade pip
  pip install -r "$REPO_ROOT/requirements.txt"
else
  echo "No requirements.txt found, skipping pip install."
fi

# Rust toolchain (if rustup not found, attempt bootstrap)
if ! command -v rustup >/dev/null 2>&1; then
  echo "rustup not found. Installing rustup (user install)..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  export PATH="$HOME/.cargo/bin:$PATH"
fi

# Print versions
echo "Git: $(git --version 2>/dev/null || echo 'not installed')"
echo "Python: $(python3 --version 2>/dev/null || echo 'not installed')"
echo "pip: $(pip --version 2>/dev/null || echo 'not installed')"
echo "g++: $(g++ --version | head -n1 2>/dev/null || echo 'not installed')"
echo "rustc: $(command -v rustc >/dev/null 2>&1 && rustc --version || echo 'not installed')"
echo "cargo: $(command -v cargo >/dev/null 2>&1 && cargo --version || echo 'not installed')"

echo "Environment setup complete."
exit 0
