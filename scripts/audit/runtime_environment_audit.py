#!/usr/bin/env python3
"""Runtime environment audit for executable portability checks."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def _is_virtualenv_active() -> bool:
    if os.getenv("VIRTUAL_ENV"):
        return True
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report() -> dict:
    python_found = shutil.which("python") is not None
    python3_found = shutil.which("python3") is not None
    pytest_found = shutil.which("pytest") is not None
    git_found = shutil.which("git") is not None
    virtualenv_active = _is_virtualenv_active()

    runtime_valid = python3_found and pytest_found and git_found

    return {
        "runtime_valid": runtime_valid,
        "timestamp": _utc_timestamp(),
        "python_found": python_found,
        "python3_found": python3_found,
        "pytest_found": pytest_found,
        "git_found": git_found,
        "virtualenv_active": virtualenv_active,
        "virtualenv_status": "active" if virtualenv_active else "inactive",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit runtime toolchain portability for audit/test execution.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/audit/runtime_environment_report.json"),
        help="Path to write JSON report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["runtime_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
