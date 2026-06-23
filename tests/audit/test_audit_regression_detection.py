#!/usr/bin/env python3
"""Tests for v1.1.5 audit regression detection."""

import json
import subprocess
from pathlib import Path


SCRIPT_PATH = Path("scripts/audit/audit_regression_detection.py")


def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")



def _seed_baseline_reports(root: Path):
    audit_dir = root / "docs" / "audit"

    _write_json(
        audit_dir / "release_integrity_report.json",
        {
            "audit_valid": True,
            "integrity_score": 1.0,
        },
    )

    _write_json(
        audit_dir / "repository_health.json",
        {
            "health_valid": True,
            "health_score": 1.0,
        },
    )

    _write_json(
        audit_dir / "release_readiness_report.json",
        {
            "release_ready": True,
            "readiness_score": 1.0,
        },
    )

    _write_json(
        audit_dir / "continuous_audit_report.json",
        {
            "monitoring_valid": True,
            "monitoring_score": 1.0,
        },
    )

    _write_json(
        audit_dir / "automated_release_validation_report.json",
        {
            "validation_valid": True,
            "validation_score": 1.0,
            "release_approved": True,
        },
    )



def _run_detector(cwd: Path):
    result = subprocess.run(
        ["python", str(SCRIPT_PATH.resolve())],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    report_path = cwd / "docs" / "audit" / "audit_regression_report.json"
    assert report_path.exists(), "Expected regression report to be generated"

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    return result, report, report_path.read_text(encoding="utf-8")



def test_cli_execution_generates_report(tmp_path):
    _seed_baseline_reports(tmp_path)

    result, report, _ = _run_detector(tmp_path)

    assert result.returncode == 0
    assert report["regression_detected"] is False



def test_report_schema(tmp_path):
    _seed_baseline_reports(tmp_path)

    _, report, _ = _run_detector(tmp_path)

    expected_keys = {
        "regression_detected",
        "regression_score",
        "integrity_regression",
        "health_regression",
        "readiness_regression",
        "monitoring_regression",
        "validation_regression",
        "baseline_valid",
    }

    assert set(report.keys()) == expected_keys



def test_baseline_comparison_no_regression(tmp_path):
    _seed_baseline_reports(tmp_path)

    _, report, _ = _run_detector(tmp_path)

    assert report == {
        "regression_detected": False,
        "regression_score": 1.0,
        "integrity_regression": False,
        "health_regression": False,
        "readiness_regression": False,
        "monitoring_regression": False,
        "validation_regression": False,
        "baseline_valid": True,
    }



def test_regression_detection(tmp_path):
    _seed_baseline_reports(tmp_path)

    _write_json(
        tmp_path / "docs" / "audit" / "repository_health.json",
        {
            "health_valid": False,
            "health_score": 0.8,
        },
    )

    result, report, _ = _run_detector(tmp_path)

    assert result.returncode == 1
    assert report["regression_detected"] is True
    assert report["health_regression"] is True
    assert report["regression_score"] == 0.8



def test_deterministic_output(tmp_path):
    _seed_baseline_reports(tmp_path)

    _, report_one, text_one = _run_detector(tmp_path)
    _, report_two, text_two = _run_detector(tmp_path)

    assert report_one == report_two
    assert text_one == text_two
