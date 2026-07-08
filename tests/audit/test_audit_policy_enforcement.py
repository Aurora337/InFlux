#!/usr/bin/env python3
"""Test suite for v1.1.7 Audit Policy Enforcement."""

import json
import subprocess
from pathlib import Path

from runtime_executable import PYTHON_EXECUTABLE


SCRIPT_PATH = Path("scripts/audit/audit_policy_enforcement.py")


POLICY_TEMPLATE = {
    "require_integrity": True,
    "require_health": True,
    "require_readiness": True,
    "require_monitoring": True,
    "require_validation": True,
    "require_regression_clear": True,
    "require_certification": True,
}


def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _seed_passing_inputs(root: Path):
    audit_dir = root / "docs" / "audit"

    _write_json(audit_dir / "audit_policy.json", POLICY_TEMPLATE)
    _write_json(audit_dir / "release_integrity_report.json", {"audit_valid": True})
    _write_json(audit_dir / "repository_health.json", {"health_valid": True})
    _write_json(audit_dir / "release_readiness_report.json", {"release_ready": True})
    _write_json(audit_dir / "continuous_audit_report.json", {"monitoring_valid": True})
    _write_json(audit_dir / "automated_release_validation_report.json", {"release_approved": True})
    _write_json(audit_dir / "audit_regression_report.json", {"regression_detected": False})
    _write_json(audit_dir / "release_certification_report.json", {"release_certified": True})


def _run_policy(root: Path):
    result = subprocess.run(
        [PYTHON_EXECUTABLE, str(SCRIPT_PATH.resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    report_path = root / "docs" / "audit" / "audit_policy_report.json"
    assert report_path.exists(), "Expected policy report to be generated"

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    report_text = report_path.read_text(encoding="utf-8")
    return result, report, report_text


def test_policy_schema(tmp_path):
    _seed_passing_inputs(tmp_path)
    _, report, _ = _run_policy(tmp_path)

    expected_keys = {
        "policy_valid",
        "policy_score",
        "policy_enforced",
        "integrity_requirement_met",
        "health_requirement_met",
        "readiness_requirement_met",
        "monitoring_requirement_met",
        "validation_requirement_met",
        "regression_requirement_met",
        "certification_requirement_met",
    }
    assert set(report.keys()) == expected_keys


def test_policy_parsing_invalid_schema(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "audit_policy.json",
        {"require_integrity": True},
    )

    result, report, _ = _run_policy(tmp_path)

    assert result.returncode == 1
    assert report["policy_valid"] is False
    assert report["policy_score"] == 0.0


def test_requirement_evaluation(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "audit_regression_report.json",
        {"regression_detected": True},
    )

    _, report, _ = _run_policy(tmp_path)

    assert report["regression_requirement_met"] is False
    assert report["policy_valid"] is False


def test_pass_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, report, _ = _run_policy(tmp_path)

    assert result.returncode == 0
    assert report["policy_valid"] is True
    assert report["policy_score"] == 1.0
    assert report["policy_enforced"] is True


def test_failure_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "release_certification_report.json",
        {"release_certified": False},
    )

    result, report, _ = _run_policy(tmp_path)

    assert result.returncode == 1
    assert report["certification_requirement_met"] is False
    assert report["policy_enforced"] is False


def test_cli_execution(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, _, _ = _run_policy(tmp_path)

    assert result.returncode == 0
    assert "policy_valid" in result.stdout
    assert "policy_enforced" in result.stdout


def test_deterministic_output(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, first_report, first_text = _run_policy(tmp_path)
    _, second_report, second_text = _run_policy(tmp_path)

    assert first_report == second_report
    assert first_text == second_text
