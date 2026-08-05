#!/usr/bin/env python3
"""Test suite for v1.2.0 Autonomous Release Governance."""

import json
import subprocess
from pathlib import Path

from influx.runtime_executable import PYTHON_EXECUTABLE


SCRIPT_PATH = Path("scripts/audit/autonomous_release_governance.py")


def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _seed_passing_inputs(root: Path):
    audit_dir = root / "docs" / "audit"

    _write_json(audit_dir / "release_integrity_report.json", {"audit_valid": True, "integrity_score": 1.0})
    _write_json(audit_dir / "repository_health.json", {"health_valid": True, "health_score": 1.0})
    _write_json(audit_dir / "release_readiness_report.json", {"release_ready": True, "readiness_score": 1.0})
    _write_json(audit_dir / "continuous_audit_report.json", {"monitoring_valid": True, "monitoring_score": 1.0})
    _write_json(
        audit_dir / "automated_release_validation_report.json",
        {"release_approved": True, "validation_score": 1.0},
    )
    _write_json(
        audit_dir / "audit_regression_report.json",
        {"regression_detected": False, "regression_score": 1.0, "baseline_valid": True},
    )
    _write_json(
        audit_dir / "release_certification_report.json",
        {"release_certified": True, "certification_score": 1.0},
    )
    _write_json(audit_dir / "audit_policy_report.json", {"policy_enforced": True, "policy_score": 1.0})
    _write_json(
        audit_dir / "governance_readiness_report.json",
        {"governance_ready": True, "governance_score": 1.0},
    )
    _write_json(
        audit_dir / "governance_compliance_report.json",
        {"compliance_valid": True, "compliance_score": 1.0},
    )


def _run_governance(root: Path):
    result = subprocess.run(
        [PYTHON_EXECUTABLE, str(SCRIPT_PATH.resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    report_path = root / "docs" / "audit" / "autonomous_release_governance_report.json"
    assert report_path.exists(), "Expected autonomous governance report to be generated"

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    report_text = report_path.read_text(encoding="utf-8")
    return result, report, report_text


def test_report_schema(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, report, _ = _run_governance(tmp_path)

    expected_keys = {
        "release_governed",
        "governance_score",
        "release_decision",
        "integrity_valid",
        "health_valid",
        "readiness_valid",
        "monitoring_valid",
        "validation_valid",
        "regression_valid",
        "certification_valid",
        "policy_valid",
        "governance_ready",
        "compliance_valid",
    }

    assert set(report.keys()) == expected_keys


def test_deterministic_output(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, first_report, first_text = _run_governance(tmp_path)
    _, second_report, second_text = _run_governance(tmp_path)

    assert first_report == second_report
    assert first_text == second_text


def test_approval_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, report, _ = _run_governance(tmp_path)

    assert result.returncode == 0
    assert report["release_governed"] is True
    assert report["governance_score"] == 1.0
    assert report["release_decision"] == "approved"


def test_rejection_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "governance_compliance_report.json",
        {"compliance_valid": False, "compliance_score": 0.9},
    )

    result, report, _ = _run_governance(tmp_path)

    assert result.returncode == 1
    assert report["release_governed"] is False
    assert report["release_decision"] == "rejected"


def test_missing_artifact_handling(tmp_path):
    _seed_passing_inputs(tmp_path)

    (tmp_path / "docs" / "audit" / "audit_policy_report.json").unlink()

    result, report, _ = _run_governance(tmp_path)

    assert result.returncode == 1
    assert report["policy_valid"] is False
    assert report["release_governed"] is False


def test_cli_execution(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, _, _ = _run_governance(tmp_path)

    assert result.returncode == 0
    assert "release_governed" in result.stdout
    assert "release_decision" in result.stdout


def test_governance_aggregation(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "audit_regression_report.json",
        {"regression_detected": True, "regression_score": 0.0, "baseline_valid": True},
    )

    _, report, _ = _run_governance(tmp_path)

    assert report["regression_valid"] is False
    assert report["release_governed"] is False
    assert report["governance_score"] == (9 / 10)
