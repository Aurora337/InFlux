#!/usr/bin/env python3
"""Test suite for v1.1.9 Governance Compliance Monitoring."""

import json
import subprocess
from pathlib import Path

from influx.runtime_executable import PYTHON_EXECUTABLE


SCRIPT_PATH = Path("scripts/audit/governance_compliance_monitor.py")


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


def _run_monitor(root: Path):
    result = subprocess.run(
        [PYTHON_EXECUTABLE, str(SCRIPT_PATH.resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    report_path = root / "docs" / "audit" / "governance_compliance_report.json"
    assert report_path.exists(), "Expected governance compliance report to be generated"

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    report_text = report_path.read_text(encoding="utf-8")
    return result, report, report_text


def test_report_schema(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, report, _ = _run_monitor(tmp_path)

    expected_keys = {
        "compliance_valid",
        "compliance_score",
        "integrity_compliant",
        "health_compliant",
        "readiness_compliant",
        "monitoring_compliant",
        "validation_compliant",
        "regression_compliant",
        "certification_compliant",
        "policy_compliant",
        "governance_ready_compliant",
    }

    assert set(report.keys()) == expected_keys


def test_pass_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, report, _ = _run_monitor(tmp_path)

    assert result.returncode == 0
    assert report["compliance_valid"] is True
    assert report["compliance_score"] == 1.0


def test_failure_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(tmp_path / "docs" / "audit" / "audit_policy_report.json", {"policy_enforced": False, "policy_score": 0.0})

    result, report, _ = _run_monitor(tmp_path)

    assert result.returncode == 1
    assert report["policy_compliant"] is False
    assert report["compliance_valid"] is False


def test_missing_report_handling(tmp_path):
    _seed_passing_inputs(tmp_path)

    (tmp_path / "docs" / "audit" / "governance_readiness_report.json").unlink()

    result, report, _ = _run_monitor(tmp_path)

    assert result.returncode == 1
    assert report["governance_ready_compliant"] is False


def test_compliance_aggregation(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "release_certification_report.json",
        {"release_certified": True, "certification_score": 0.75},
    )

    _, report, _ = _run_monitor(tmp_path)

    assert report["certification_compliant"] is False
    assert report["compliance_valid"] is False
    assert report["compliance_score"] == (8 / 9)


def test_cli_execution(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, _, _ = _run_monitor(tmp_path)

    assert result.returncode == 0
    assert "compliance_valid" in result.stdout
    assert "compliance_score" in result.stdout


def test_deterministic_output(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, first_report, first_text = _run_monitor(tmp_path)
    _, second_report, second_text = _run_monitor(tmp_path)

    assert first_report == second_report
    assert first_text == second_text
