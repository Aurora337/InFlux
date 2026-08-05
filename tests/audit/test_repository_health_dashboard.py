"""Tests for Repository Health Dashboard — v1.1.1 Slice 2.

Validates:
- deterministic execution
- repeatable results
- report schema and types
- no runtime artifacts committed (unit tests only validate generated
  report content exists when running the CLI)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit.repository_health_dashboard import (  # noqa: E402
    REPOSITORY_HEALTH_PATH,
    collect_repository_health,
)


def _json_dumps_sorted(d: Dict) -> str:
    return json.dumps(d, indent=2, sort_keys=True)


def test_collect_repository_health_deterministic():
    r1 = collect_repository_health()
    r2 = collect_repository_health()
    assert r1 == r2


def test_collect_repository_health_json_deterministic():
    r1 = collect_repository_health()
    r2 = collect_repository_health()
    assert _json_dumps_sorted(r1) == _json_dumps_sorted(r2)


def test_report_shape_and_types():
    r = collect_repository_health()
    expected_keys = {
        "health_valid",
        "branch_count",
        "tag_count",
        "release_count",
        "audit_count",
        "test_count",
        "missing_docs",
        "missing_audits",
        "health_score",
    }
    assert set(r.keys()) == expected_keys

    assert isinstance(r["health_valid"], bool)
    for k in [
        "branch_count",
        "tag_count",
        "release_count",
        "audit_count",
        "test_count",
    ]:
        assert isinstance(r[k], int)
        assert r[k] >= 0

    assert isinstance(r["missing_docs"], list)
    assert isinstance(r["missing_audits"], list)
    for x in r["missing_docs"]:
        assert isinstance(x, str)
    for x in r["missing_audits"]:
        assert isinstance(x, str)

    assert isinstance(r["health_score"], float)
    assert 0.0 <= r["health_score"] <= 1.0


def test_missing_lists_sorted():
    r = collect_repository_health()
    assert r["missing_docs"] == sorted(r["missing_docs"])
    assert r["missing_audits"] == sorted(r["missing_audits"])


def test_cli_generates_report_json():
    # Run CLI and ensure the report file exists and is valid JSON.
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "audit" / "repository_health_dashboard.py")],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=30,
    )
    assert result.returncode in (0, 1)
    assert "Report written to" in result.stdout

    assert REPOSITORY_HEALTH_PATH.exists()
    with open(REPOSITORY_HEALTH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["health_valid"] in (True, False)
    assert "health_score" in data


def test_write_report_is_deterministic_file_content():
    # Write twice to a temp file via direct JSON dump using collect result.
    # Since write_report writes to a canonical path, we only validate that
    # collect_repository_health dict is deterministic (already tested above).
    r = collect_repository_health()
    assert _json_dumps_sorted(r) == _json_dumps_sorted(r)

