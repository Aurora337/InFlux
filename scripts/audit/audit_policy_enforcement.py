#!/usr/bin/env python3
"""
Audit Policy Enforcement - v1.1.7

Applies centralized policy rules to prior audit reports and emits a
deterministic enforcement decision.
"""

import argparse
import json
import sys
from pathlib import Path


POLICY_PATH = "docs/audit/audit_policy.json"
REPORT_PATH = "docs/audit/audit_policy_report.json"


def load_json(path: Path):
    """Load JSON object from disk."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else None
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None


def read_bool_field(data, field):
    """Read strict bool field from a JSON object."""
    if not isinstance(data, dict):
        return False
    value = data.get(field)
    return value if isinstance(value, bool) else False


def load_policy(root: Path):
    """Load and validate deterministic policy schema."""
    policy = load_json(root / POLICY_PATH)
    required_keys = [
        "require_integrity",
        "require_health",
        "require_readiness",
        "require_monitoring",
        "require_validation",
        "require_regression_clear",
        "require_certification",
    ]

    if not isinstance(policy, dict):
        return None, False

    for key in required_keys:
        if not isinstance(policy.get(key), bool):
            return None, False

    return policy, True


def check_requirement(required, condition):
    """Requirement passes if disabled, otherwise condition must be true."""
    if not required:
        return True
    return bool(condition)


def build_policy_report(root: Path):
    """Build deterministic policy enforcement report."""
    policy, policy_schema_valid = load_policy(root)

    if not policy_schema_valid:
        return {
            "policy_valid": False,
            "policy_score": 0.0,
            "policy_enforced": False,
            "integrity_requirement_met": False,
            "health_requirement_met": False,
            "readiness_requirement_met": False,
            "monitoring_requirement_met": False,
            "validation_requirement_met": False,
            "regression_requirement_met": False,
            "certification_requirement_met": False,
        }

    integrity_report = load_json(root / "docs/audit/release_integrity_report.json")
    health_report = load_json(root / "docs/audit/repository_health.json")
    readiness_report = load_json(root / "docs/audit/release_readiness_report.json")
    monitoring_report = load_json(root / "docs/audit/continuous_audit_report.json")
    validation_report = load_json(root / "docs/audit/automated_release_validation_report.json")
    regression_report = load_json(root / "docs/audit/audit_regression_report.json")
    certification_report = load_json(root / "docs/audit/release_certification_report.json")

    integrity_requirement_met = check_requirement(
        policy["require_integrity"],
        read_bool_field(integrity_report, "audit_valid"),
    )
    health_requirement_met = check_requirement(
        policy["require_health"],
        read_bool_field(health_report, "health_valid"),
    )
    readiness_requirement_met = check_requirement(
        policy["require_readiness"],
        read_bool_field(readiness_report, "release_ready"),
    )
    monitoring_requirement_met = check_requirement(
        policy["require_monitoring"],
        read_bool_field(monitoring_report, "monitoring_valid"),
    )
    validation_requirement_met = check_requirement(
        policy["require_validation"],
        read_bool_field(validation_report, "release_approved"),
    )

    regression_clear = not read_bool_field(regression_report, "regression_detected")
    regression_requirement_met = check_requirement(
        policy["require_regression_clear"],
        regression_clear,
    )

    certification_requirement_met = check_requirement(
        policy["require_certification"],
        read_bool_field(certification_report, "release_certified"),
    )

    checks = [
        integrity_requirement_met,
        health_requirement_met,
        readiness_requirement_met,
        monitoring_requirement_met,
        validation_requirement_met,
        regression_requirement_met,
        certification_requirement_met,
    ]

    policy_valid = all(checks)
    policy_score = sum(checks) / float(len(checks))

    return {
        "policy_valid": policy_valid,
        "policy_score": policy_score,
        "policy_enforced": policy_valid,
        "integrity_requirement_met": integrity_requirement_met,
        "health_requirement_met": health_requirement_met,
        "readiness_requirement_met": readiness_requirement_met,
        "monitoring_requirement_met": monitoring_requirement_met,
        "validation_requirement_met": validation_requirement_met,
        "regression_requirement_met": regression_requirement_met,
        "certification_requirement_met": certification_requirement_met,
    }


def write_report(root: Path, report):
    """Write deterministic policy report JSON."""
    out_path = root / REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Audit policy enforcement")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_policy_report(root)
    out_path = write_report(root, report)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"Report written to: {out_path}")

    return 0 if report["policy_enforced"] else 1


if __name__ == "__main__":
    sys.exit(main())
