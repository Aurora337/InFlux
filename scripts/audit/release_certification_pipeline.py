#!/usr/bin/env python3
"""
Release Certification Pipeline - v1.1.6

Aggregates all audit layers into a final deterministic certification decision.
"""

import argparse
import json
import sys
from pathlib import Path


INPUT_REPORTS = {
    "integrity": ("docs/audit/release_integrity_report.json", "audit_valid"),
    "health": ("docs/audit/repository_health.json", "health_valid"),
    "readiness": ("docs/audit/release_readiness_report.json", "release_ready"),
    "monitoring": ("docs/audit/continuous_audit_report.json", "monitoring_valid"),
    "validation": ("docs/audit/automated_release_validation_report.json", "release_approved"),
    "regression": ("docs/audit/audit_regression_report.json", "regression_detected"),
}


OUTPUT_PATH = "docs/audit/release_certification_report.json"


def load_json(path: Path):
    """Load JSON object from file path."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else None
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None


def read_bool_field(data, field):
    """Read strict boolean field from report data."""
    if not isinstance(data, dict):
        return False
    value = data.get(field)
    return value if isinstance(value, bool) else False


def build_certification_report(root: Path):
    """Build deterministic release certification report."""
    reports = {
        name: load_json(root / rel_path)
        for name, (rel_path, _) in INPUT_REPORTS.items()
    }

    integrity_valid = read_bool_field(reports["integrity"], INPUT_REPORTS["integrity"][1])
    health_valid = read_bool_field(reports["health"], INPUT_REPORTS["health"][1])
    readiness_valid = read_bool_field(reports["readiness"], INPUT_REPORTS["readiness"][1])
    monitoring_valid = read_bool_field(reports["monitoring"], INPUT_REPORTS["monitoring"][1])
    validation_valid = read_bool_field(reports["validation"], INPUT_REPORTS["validation"][1])

    regression_detected = read_bool_field(reports["regression"], INPUT_REPORTS["regression"][1])
    regression_valid = not regression_detected

    checks = [
        integrity_valid,
        health_valid,
        readiness_valid,
        monitoring_valid,
        validation_valid,
        regression_valid,
    ]

    certification_valid = all(checks)
    certification_score = sum(checks) / float(len(checks))

    return {
        "certification_valid": certification_valid,
        "certification_score": certification_score,
        "release_certified": certification_valid,
        "integrity_valid": integrity_valid,
        "health_valid": health_valid,
        "readiness_valid": readiness_valid,
        "monitoring_valid": monitoring_valid,
        "validation_valid": validation_valid,
        "regression_valid": regression_valid,
    }


def write_report(root: Path, report):
    """Write deterministic certification JSON report."""
    out_path = root / OUTPUT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Release certification pipeline")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_certification_report(root)
    out_path = write_report(root, report)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"Report written to: {out_path}")

    return 0 if report["release_certified"] else 1


if __name__ == "__main__":
    sys.exit(main())
