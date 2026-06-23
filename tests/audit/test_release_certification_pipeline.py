#!/usr/bin/env python3
"""Test suite for v1.1.6 Release Certification Pipeline."""

import json
import subprocess
from pathlib import Path


SCRIPT_PATH = Path("scripts/audit/release_certification_pipeline.py")


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
    _write_json(
        audit_dir / "automated_release_validation_report.json",
        {"release_approved": True},
    )
    _write_json(audit_dir / "audit_regression_report.json", {"regression_detected": False})


def _run_pipeline(root: Path):
    result = subprocess.run(
        ["python", str(SCRIPT_PATH.resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    report_path = root / "docs" / "audit" / "release_certification_report.json"
    assert report_path.exists(), "Expected certification report to be generated"

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    report_text = report_path.read_text(encoding="utf-8")
    return result, report, report_text


def test_report_schema(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, report, _ = _run_pipeline(tmp_path)

    expected_keys = {
        "certification_valid",
        "certification_score",
        "release_certified",
        "integrity_valid",
        "health_valid",
        "readiness_valid",
        "monitoring_valid",
        "validation_valid",
        "regression_valid",
    }

    assert set(report.keys()) == expected_keys


def test_deterministic_output(tmp_path):
    _seed_passing_inputs(tmp_path)

    _, first_report, first_text = _run_pipeline(tmp_path)
    _, second_report, second_text = _run_pipeline(tmp_path)

    assert first_report == second_report
    assert first_text == second_text


def test_pass_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, report, _ = _run_pipeline(tmp_path)

    assert result.returncode == 0
    assert report["certification_valid"] is True
    assert report["certification_score"] == 1.0
    assert report["release_certified"] is True


def test_failure_path(tmp_path):
    _seed_passing_inputs(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "audit_regression_report.json",
        {"regression_detected": True},
    )

    result, report, _ = _run_pipeline(tmp_path)

    assert result.returncode == 1
    assert report["certification_valid"] is False
    assert report["release_certified"] is False
    assert report["regression_valid"] is False


def test_cli_execution(tmp_path):
    _seed_passing_inputs(tmp_path)

    result, _, _ = _run_pipeline(tmp_path)

    assert result.returncode == 0
    assert "certification_valid" in result.stdout
    assert "release_certified" in result.stdout


def test_certification_aggregation(tmp_path):
    _seed_passing_inputs(tmp_path)

    # Flip one gate to ensure score reflects 5/6 pass ratio.
    _write_json(
        tmp_path / "docs" / "audit" / "continuous_audit_report.json",
        {"monitoring_valid": False},
    )

    _, report, _ = _run_pipeline(tmp_path)

    assert report["monitoring_valid"] is False
    assert report["certification_valid"] is False
    assert report["certification_score"] == (5 / 6)
