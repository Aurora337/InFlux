#!/usr/bin/env python3
"""
Governance Compliance Monitoring - v1.1.9

Continuously verifies that all governance components remain compliant.
"""

import argparse
import json
import sys
from pathlib import Path


REPORT_SPECS = {
    "integrity": {
        "path": "docs/audit/release_integrity_report.json",
        "status_field": "audit_valid",
        "expected_status": True,
        "score_field": "integrity_score",
        "expected_score": 1.0,
        "required_fields": ["audit_valid", "integrity_score"],
    },
    "health": {
        "path": "docs/audit/repository_health.json",
        "status_field": "health_valid",
        "expected_status": True,
        "score_field": "health_score",
        "expected_score": 1.0,
        "required_fields": ["health_valid", "health_score"],
    },
    "readiness": {
        "path": "docs/audit/release_readiness_report.json",
        "status_field": "release_ready",
        "expected_status": True,
        "score_field": "readiness_score",
        "expected_score": 1.0,
        "required_fields": ["release_ready", "readiness_score"],
    },
    "monitoring": {
        "path": "docs/audit/continuous_audit_report.json",
        "status_field": "monitoring_valid",
        "expected_status": True,
        "score_field": "monitoring_score",
        "expected_score": 1.0,
        "required_fields": ["monitoring_valid", "monitoring_score"],
    },
    "validation": {
        "path": "docs/audit/automated_release_validation_report.json",
        "status_field": "release_approved",
        "expected_status": True,
        "score_field": "validation_score",
        "expected_score": 1.0,
        "required_fields": ["release_approved", "validation_score"],
    },
    "regression": {
        "path": "docs/audit/audit_regression_report.json",
        "status_field": "regression_detected",
        "expected_status": False,
        "score_field": "regression_score",
        "expected_score": 1.0,
        "required_fields": ["regression_detected", "regression_score", "baseline_valid"],
    },
    "certification": {
        "path": "docs/audit/release_certification_report.json",
        "status_field": "release_certified",
        "expected_status": True,
        "score_field": "certification_score",
        "expected_score": 1.0,
        "required_fields": ["release_certified", "certification_score"],
    },
    "policy": {
        "path": "docs/audit/audit_policy_report.json",
        "status_field": "policy_enforced",
        "expected_status": True,
        "score_field": "policy_score",
        "expected_score": 1.0,
        "required_fields": ["policy_enforced", "policy_score"],
    },
    "governance_ready": {
        "path": "docs/audit/governance_readiness_report.json",
        "status_field": "governance_ready",
        "expected_status": True,
        "score_field": "governance_score",
        "expected_score": 1.0,
        "required_fields": ["governance_ready", "governance_score"],
    },
}

OUTPUT_PATH = "docs/audit/governance_compliance_report.json"


def load_json(path: Path):
    """Load JSON object from disk."""
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


def read_score_field(data, field):
    """Read a deterministic numeric score from a JSON object."""
    if not isinstance(data, dict):
        return None
    value = data.get(field)
    return value if isinstance(value, (int, float)) else None


def evaluate_compliance(report, spec):
    """Evaluate one governance component against compliance requirements."""
    if report is None:
        return False

    for field in spec["required_fields"]:
        if field not in report:
            return False

    status_value = read_bool_field(report, spec["status_field"])
    if status_value != spec["expected_status"]:
        return False

    score_value = read_score_field(report, spec["score_field"])
    if score_value is None:
        return False

    return float(score_value) == float(spec["expected_score"])


def build_compliance_report(root: Path):
    """Build deterministic governance compliance report."""
    reports = {
        name: load_json(root / spec["path"])
        for name, spec in REPORT_SPECS.items()
    }

    integrity_compliant = evaluate_compliance(reports["integrity"], REPORT_SPECS["integrity"])
    health_compliant = evaluate_compliance(reports["health"], REPORT_SPECS["health"])
    readiness_compliant = evaluate_compliance(reports["readiness"], REPORT_SPECS["readiness"])
    monitoring_compliant = evaluate_compliance(reports["monitoring"], REPORT_SPECS["monitoring"])
    validation_compliant = evaluate_compliance(reports["validation"], REPORT_SPECS["validation"])
    regression_compliant = evaluate_compliance(reports["regression"], REPORT_SPECS["regression"])
    certification_compliant = evaluate_compliance(reports["certification"], REPORT_SPECS["certification"])
    policy_compliant = evaluate_compliance(reports["policy"], REPORT_SPECS["policy"])
    governance_ready_compliant = evaluate_compliance(
        reports["governance_ready"],
        REPORT_SPECS["governance_ready"],
    )

    checks = [
        integrity_compliant,
        health_compliant,
        readiness_compliant,
        monitoring_compliant,
        validation_compliant,
        regression_compliant,
        certification_compliant,
        policy_compliant,
        governance_ready_compliant,
    ]

    compliance_valid = all(checks)
    compliance_score = sum(checks) / float(len(checks))

    return {
        "compliance_valid": compliance_valid,
        "compliance_score": compliance_score,
        "integrity_compliant": integrity_compliant,
        "health_compliant": health_compliant,
        "readiness_compliant": readiness_compliant,
        "monitoring_compliant": monitoring_compliant,
        "validation_compliant": validation_compliant,
        "regression_compliant": regression_compliant,
        "certification_compliant": certification_compliant,
        "policy_compliant": policy_compliant,
        "governance_ready_compliant": governance_ready_compliant,
    }


def write_report(root: Path, report):
    """Write deterministic governance compliance JSON report."""
    out_path = root / OUTPUT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Governance compliance monitoring")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_compliance_report(root)
    out_path = write_report(root, report)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"Report written to: {out_path}")

    return 0 if report["compliance_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
