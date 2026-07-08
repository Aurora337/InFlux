#!/usr/bin/env python3
"""
Governance Readiness Validation - v1.1.8

Validates that the full governance stack exists, is valid, and is enforceable.
"""

import argparse
import json
import sys
from pathlib import Path


INPUT_FILES = {
    "integrity": ("docs/audit/release_integrity_report.json", "audit_valid"),
    "health": ("docs/audit/repository_health.json", "health_valid"),
    "readiness": ("docs/audit/release_readiness_report.json", "release_ready"),
    "monitoring": ("docs/audit/continuous_audit_report.json", "monitoring_valid"),
    "validation": ("docs/audit/automated_release_validation_report.json", "release_approved"),
    "regression": ("docs/audit/audit_regression_report.json", "regression_detected"),
    "certification": ("docs/audit/release_certification_report.json", "release_certified"),
    "policy": ("docs/audit/audit_policy_report.json", "policy_enforced"),
}

OUTPUT_PATH = "docs/audit/governance_readiness_report.json"


def load_json(path: Path):
    """Load a JSON object from disk."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else None
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None


def read_bool_field(data, field):
    """Read a strict boolean field from a JSON object."""
    if not isinstance(data, dict):
        return False
    value = data.get(field)
    return value if isinstance(value, bool) else False


def evaluate_governed(report, field):
    """A governance component is governed when it exists, is schema-valid, and passes."""
    return report is not None and read_bool_field(report, field)


def build_governance_readiness_report(root: Path):
    """Build deterministic governance readiness report."""
    reports = {
        name: load_json(root / rel_path)
        for name, (rel_path, _) in INPUT_FILES.items()
    }

    integrity_governed = evaluate_governed(reports["integrity"], INPUT_FILES["integrity"][1])
    health_governed = evaluate_governed(reports["health"], INPUT_FILES["health"][1])
    readiness_governed = evaluate_governed(reports["readiness"], INPUT_FILES["readiness"][1])
    monitoring_governed = evaluate_governed(reports["monitoring"], INPUT_FILES["monitoring"][1])
    validation_governed = evaluate_governed(reports["validation"], INPUT_FILES["validation"][1])

    regression_report = reports["regression"]
    regression_governed = regression_report is not None and not read_bool_field(
        regression_report,
        INPUT_FILES["regression"][1],
    )

    certification_governed = evaluate_governed(reports["certification"], INPUT_FILES["certification"][1])
    policy_governed = evaluate_governed(reports["policy"], INPUT_FILES["policy"][1])

    checks = [
        integrity_governed,
        health_governed,
        readiness_governed,
        monitoring_governed,
        validation_governed,
        regression_governed,
        certification_governed,
        policy_governed,
    ]

    governance_ready = all(checks)
    governance_score = sum(checks) / float(len(checks))

    return {
        "governance_ready": governance_ready,
        "governance_score": governance_score,
        "integrity_governed": integrity_governed,
        "health_governed": health_governed,
        "readiness_governed": readiness_governed,
        "monitoring_governed": monitoring_governed,
        "validation_governed": validation_governed,
        "regression_governed": regression_governed,
        "certification_governed": certification_governed,
        "policy_governed": policy_governed,
    }


def write_report(root: Path, report):
    """Write deterministic governance readiness JSON report."""
    out_path = root / OUTPUT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Governance readiness validation")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_governance_readiness_report(root)
    out_path = write_report(root, report)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"Report written to: {out_path}")

    return 0 if report["governance_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
