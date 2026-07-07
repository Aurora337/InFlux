#!/usr/bin/env python3
"""Test suite for v1.1.8 Governance Readiness Validation."""

import json
import subprocess
from pathlib import Path

from runtime_executable import PYTHON_EXECUTABLE


SCRIPT_PATH = Path("scripts/audit/governance_readiness_validation.py")


def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _seed_passing_inputs(root: Path):
    audit_dir = root / "docs" / "audit"

    _write_json(audit_dir / "release_integrity_report.json", {"audit_valid": True})
    _write_json(audit_dir / "repository_health.json", {"health_valid": True})
    _write_json(audit_dir / "release_readiness_report.json", {"release_ready": True})
    _write_json(audit_dir / "continuous_audit_report.json", {"monitoring_valid": True})
    _write_json(audit_dir / "automated_release_validation_report.json", {"release_approved": True})
    _write_json(audit_dir / "audit_regression_report.json", {"regression_detected": False})
    _write_json(audit_dir / "release_certification_report.json", {"release_certified": True})
    _write_json(audit_dir / "audit_policy_report.json", {"policy_enforced": True})


def _run_validator(root: Path):
    result = subprocess.run(
        [PYTHON_EXECUTABLE, str(SCRIPT_PATH.resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    report_path = root / "docs" / "audit" / "governance_readiness_report.json"
    assert report_path.exists(), "Expected governance readiness report to be generated"

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    report_text = report_path.read_text(encoding="utf-8")
    return result, report, report_text


def test_report_schema(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, report, _ = _run_validator(tmp_path)

    expected_keys = {
        "governance_ready",
        "governance_score",
        "integrity_governed",
        "health_governed",
        "readiness_governed",
        "monitoring_governed",
        "validation_governed",
        "regression_governed",
        "certification_governed",
        "policy_governed",
    }

    assert set(report.keys()) == expected_keys


def test_required_field_validation(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(tmp_path / "docs" / "audit" / "audit_policy_report.json", {})

    _, report, _ = _run_validator(tmp_path)

    assert report["policy_governed"] is False
    assert report["governance_ready"] is False


def test_pass_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, report, _ = _run_validator(tmp_path)

    assert result.returncode == 0
    assert report["governance_ready"] is True
    assert report["governance_score"] == 1.0


def test_missing_report_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    (tmp_path / "docs" / "audit" / "release_certification_report.json").unlink()

    result, report, _ = _run_validator(tmp_path)

    assert result.returncode == 1
    assert report["certification_governed"] is False
    assert report["governance_ready"] is False


def test_failure_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(tmp_path / "docs" / "audit" / "release_integrity_report.json", {"audit_valid": False})

    result, report, _ = _run_validator(tmp_path)

    assert result.returncode == 1
    assert report["integrity_governed"] is False
    assert report["governance_ready"] is False


def test_cli_execution(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, _, _ = _run_validator(tmp_path)

    assert result.returncode == 0
    assert "governance_ready" in result.stdout
    assert "governance_score" in result.stdout


def test_deterministic_output(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, first_report, first_text = _run_validator(tmp_path)
    _, second_report, second_text = _run_validator(tmp_path)

    assert first_report == second_report
    assert first_text == second_text
