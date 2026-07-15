"""Runtime executable resolution helpers for portable subprocess calls."""

from __future__ import annotations

import shutil
import sys
from typing import List

__all__ = ["PYTHON_EXECUTABLE", "PYTEST_EXECUTABLE", "python_cmd", "pytest_cmd"]
PYTHON_EXECUTABLE: str = (
    sys.executable
    or shutil.which("python")
    or shutil.which("python3")
    or "python"
)
PYTEST_EXECUTABLE = shutil.which("pytest")

if not PYTHON_EXECUTABLE:
    raise RuntimeError("No Python executable found. Expected 'python' or 'python3' in PATH.")


def python_cmd(*args: str) -> List[str]:
    """Build a subprocess command prefixed with the resolved Python executable."""
    return [PYTHON_EXECUTABLE, *args]


def pytest_cmd(*args: str) -> List[str]:
    """Build a portable pytest invocation, preferring `python -m pytest`."""
    if PYTEST_EXECUTABLE:
        return [PYTEST_EXECUTABLE, *args]
    return python_cmd("-m", "pytest", *args)
