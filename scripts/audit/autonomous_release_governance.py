#!/usr/bin/env python3
"""
Autonomous Release Governance - v1.2.0

Aggregates the full Sync Ops Audit governance chain into the final release decision.
"""

import argparse
import json
import sys
from pathlib import Path


GOVERNANCE_SPECS = {
    "integrity": {
        "path": "docs/audit/release_integrity_report.json",
        "status_field": "audit_valid",
        "required_status": True,
        "score_field": "integrity_score",
        "required_score": 1.0,
        "required_fields": ["audit_valid", "integrity_score"],
    },
    "health": {
        "path": "docs/audit/repository_health.json",
        "status_field": "health_valid",
        "required_status": True,
        "score_field": "health_score",
        "required_score": 1.0,
        "required_fields": ["health_valid", "health_score"],
    },
    "readiness": {
        "path": "docs/audit/release_readiness_report.json",
        "status_field": "release_ready",
        "required_status": True,
        "score_field": "readiness_score",
        "required_score": 1.0,
        "required_fields": ["release_ready", "readiness_score"],
    },
    "monitoring": {
        "path": "docs/audit/continuous_audit_report.json",
        "status_field": "monitoring_valid",
        "required_status": True,
        "score_field": "monitoring_score",
        "required_score": 1.0,
        "required_fields": ["monitoring_valid", "monitoring_score"],
    },
    "validation": {
        "path": "docs/audit/automated_release_validation_report.json",
        "status_field": "release_approved",
        "required_status": True,
        "score_field": "validation_score",
        "required_score": 1.0,
        "required_fields": ["release_approved", "validation_score"],
    },
    "regression": {
        "path": "docs/audit/audit_regression_report.json",
        "status_field": "regression_detected",
        "required_status": False,
        "score_field": "regression_score",
        "required_score": 1.0,
        "required_fields": ["regression_detected", "regression_score", "baseline_valid"],
    },
    "certification": {
        "path": "docs/audit/release_certification_report.json",
        "status_field": "release_certified",
        "required_status": True,
        "score_field": "certification_score",
        "required_score": 1.0,
        "required_fields": ["release_certified", "certification_score"],
    },
    "policy": {
        "path": "docs/audit/audit_policy_report.json",
        "status_field": "policy_enforced",
        "required_status": True,
        "score_field": "policy_score",
        "required_score": 1.0,
        "required_fields": ["policy_enforced", "policy_score"],
    },
    "governance_ready": {
        "path": "docs/audit/governance_readiness_report.json",
        "status_field": "governance_ready",
        "required_status": True,
        "score_field": "governance_score",
        "required_score": 1.0,
        "required_fields": ["governance_ready", "governance_score"],
    },
    "compliance": {
        "path": "docs/audit/governance_compliance_report.json",
        "status_field": "compliance_valid",
        "required_status": True,
        "score_field": "compliance_score",
        "required_score": 1.0,
        "required_fields": ["compliance_valid", "compliance_score"],
    },
}

OUTPUT_PATH = "docs/audit/autonomous_release_governance_report.json"


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
    """Read a deterministic numeric field from a JSON object."""
    if not isinstance(data, dict):
        return None
    value = data.get(field)
    return value if isinstance(value, (int, float)) else None


def evaluate_governance(report, spec):
    """Evaluate one governance artifact against the authoritative release criteria."""
    if report is None:
        return False

    for field in spec["required_fields"]:
        if field not in report:
            return False

    status_value = read_bool_field(report, spec["status_field"])
    if status_value != spec["required_status"]:
        return False

    score_value = read_score_field(report, spec["score_field"])
    if score_value is None:
        return False

    return float(score_value) == float(spec["required_score"])


def build_governance_report(root: Path):
    """Build deterministic autonomous governance report."""
    reports = {
        name: load_json(root / spec["path"])
        for name, spec in GOVERNANCE_SPECS.items()
    }

    integrity_valid = evaluate_governance(reports["integrity"], GOVERNANCE_SPECS["integrity"])
    health_valid = evaluate_governance(reports["health"], GOVERNANCE_SPECS["health"])
    readiness_valid = evaluate_governance(reports["readiness"], GOVERNANCE_SPECS["readiness"])
    monitoring_valid = evaluate_governance(reports["monitoring"], GOVERNANCE_SPECS["monitoring"])
    validation_valid = evaluate_governance(reports["validation"], GOVERNANCE_SPECS["validation"])
    regression_valid = evaluate_governance(reports["regression"], GOVERNANCE_SPECS["regression"])
    certification_valid = evaluate_governance(reports["certification"], GOVERNANCE_SPECS["certification"])
    policy_valid = evaluate_governance(reports["policy"], GOVERNANCE_SPECS["policy"])
    governance_ready = evaluate_governance(reports["governance_ready"], GOVERNANCE_SPECS["governance_ready"])
    compliance_valid = evaluate_governance(reports["compliance"], GOVERNANCE_SPECS["compliance"])

    checks = [
        integrity_valid,
        health_valid,
        readiness_valid,
        monitoring_valid,
        validation_valid,
        regression_valid,
        certification_valid,
        policy_valid,
        governance_ready,
        compliance_valid,
    ]

    release_governed = all(checks)
    governance_score = sum(checks) / float(len(checks))
    release_decision = "approved" if release_governed else "rejected"

    return {
        "release_governed": release_governed,
        "governance_score": governance_score,
        "release_decision": release_decision,
        "integrity_valid": integrity_valid,
        "health_valid": health_valid,
        "readiness_valid": readiness_valid,
        "monitoring_valid": monitoring_valid,
        "validation_valid": validation_valid,
        "regression_valid": regression_valid,
        "certification_valid": certification_valid,
        "policy_valid": policy_valid,
        "governance_ready": governance_ready,
        "compliance_valid": compliance_valid,
    }


def write_report(root: Path, report):
    """Write deterministic autonomous governance JSON report."""
    out_path = root / OUTPUT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Autonomous release governance")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_governance_report(root)
    out_path = write_report(root, report)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"Report written to: {out_path}")

    return 0 if report["release_governed"] else 1


if __name__ == "__main__":
    sys.exit(main())
