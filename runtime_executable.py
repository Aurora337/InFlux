"""Runtime executable resolution helpers for portable subprocess calls."""

from __future__ import annotations

import shutil
from typing import List

PYTHON_EXECUTABLE = shutil.which("python") or shutil.which("python3")

if not PYTHON_EXECUTABLE:
    raise RuntimeError("No Python executable found. Expected 'python' or 'python3' in PATH.")


def python_cmd(*args: str) -> List[str]:
    """Build a subprocess command prefixed with the resolved Python executable."""
    return [PYTHON_EXECUTABLE, *args]
