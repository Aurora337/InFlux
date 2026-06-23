#!/usr/bin/env python3
"""
Automated Release Validation - v1.1.4 Slice 1

Consumes outputs from all prior audit layers:
- Release Integrity Audit (v1.1.1)
- Repository Health Dashboard (v1.1.1)
- Release Readiness Audit (v1.1.2)
- Continuous Audit Monitor (v1.1.3)

Produces deterministic validation output for release approval gate.

This is the final enforcement layer of the Sync Ops Audit ladder.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_report(report_path):
    """Load and validate JSON report."""
    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def check_integrity_report():
    """Validate release integrity report exists and is valid."""
    report = load_report("docs/audit/release_integrity_report.json")
    if not report:
        return False, "Integrity report missing"
    
    # Check for required fields
    if not isinstance(report.get("audit_valid"), bool):
        return False, "Integrity report missing audit_valid"
    
    if report.get("integrity_score", 0) != 1.0:
        return False, f"Integrity score not 1.0: {report.get('integrity_score')}"
    
    if not report.get("audit_valid"):
        return False, "Integrity audit failed"
    
    return True, "Integrity OK"


def check_health_report():
    """Validate repository health report exists and is valid."""
    report = load_report("docs/audit/repository_health.json")
    if not report:
        return False, "Health report missing"
    
    # Check for required fields
    if not isinstance(report.get("health_valid"), bool):
        return False, "Health report missing health_valid"
    
    if report.get("health_score", 0) != 1.0:
        return False, f"Health score not 1.0: {report.get('health_score')}"
    
    if not report.get("health_valid"):
        return False, "Health audit failed"
    
    return True, "Health OK"


def check_readiness_report():
    """Validate release readiness report exists and is valid."""
    report = load_report("docs/audit/release_readiness_report.json")
    if not report:
        return False, "Readiness report missing"
    
    # Check for required fields
    if not isinstance(report.get("release_ready"), bool):
        return False, "Readiness report missing release_ready"
    
    if report.get("readiness_score", 0) != 1.0:
        return False, f"Readiness score not 1.0: {report.get('readiness_score')}"
    
    if not report.get("release_ready"):
        return False, "Release not ready"
    
    # Validate all 7 checks passed
    checks = report.get("checks", {})
    required_checks = [
        "tests_valid",
        "audit_valid",
        "release_notes_present",
        "tags_consistent",
        "working_tree_clean",
        "no_generated_artifacts",
        "main_has_merge"
    ]
    
    for check in required_checks:
        if not checks.get(check):
            return False, f"Readiness check failed: {check}"
    
    return True, "Readiness OK"


def check_monitoring_report():
    """Validate continuous monitoring report exists and is valid."""
    report = load_report("docs/audit/continuous_audit_report.json")
    if not report:
        return False, "Monitoring report missing"
    
    # Check for required fields
    if not isinstance(report.get("monitoring_valid"), bool):
        return False, "Monitoring report missing monitoring_valid"
    
    if report.get("monitoring_score", 0) != 1.0:
        return False, f"Monitoring score not 1.0: {report.get('monitoring_score')}"
    
    if not report.get("monitoring_valid"):
        return False, "Monitoring detected drift"
    
    # Validate no drifts detected
    drift = report.get("drift_detection", {})
    if drift.get("audit_drift_detected"):
        return False, "Audit drift detected"
    if drift.get("health_drift_detected"):
        return False, "Health drift detected"
    if drift.get("readiness_drift_detected"):
        return False, "Readiness drift detected"
    if drift.get("working_tree_drift_detected"):
        return False, "Working tree drift detected"
    
    return True, "Monitoring OK"


def generate_validation_report():
    """Run all validation checks and generate report."""
    print("\n📋 Automated Release Validation")
    
    # Run all validation checks
    integrity_valid, integrity_msg = check_integrity_report()
    health_valid, health_msg = check_health_report()
    readiness_valid, readiness_msg = check_readiness_report()
    monitoring_valid, monitoring_msg = check_monitoring_report()
    
    # Determine overall validation
    all_valid = integrity_valid and health_valid and readiness_valid and monitoring_valid
    validation_score = sum([integrity_valid, health_valid, readiness_valid, monitoring_valid]) / 4.0
    
    # Build report
    report = {
        "validation_valid": all_valid,
        "validation_score": validation_score,
        "release_integrity_valid": integrity_valid,
        "repository_health_valid": health_valid,
        "release_readiness_valid": readiness_valid,
        "continuous_monitoring_valid": monitoring_valid,
        "release_approved": all_valid,
        "checks": {
            "integrity": {
                "valid": integrity_valid,
                "message": integrity_msg
            },
            "health": {
                "valid": health_valid,
                "message": health_msg
            },
            "readiness": {
                "valid": readiness_valid,
                "message": readiness_msg
            },
            "monitoring": {
                "valid": monitoring_valid,
                "message": monitoring_msg
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    
    # Display results
    status_icon = "✅" if all_valid else "⚠️"
    print(f"{status_icon} Automated Release Validation")
    print(f"   Score: {int(validation_score * 100)}%")
    print(f"   Approved: {all_valid}")
    print()
    print("Validation Checks:")
    print(f"  {'✓' if integrity_valid else '✗'} integrity: {integrity_msg}")
    print(f"  {'✓' if health_valid else '✗'} health: {health_msg}")
    print(f"  {'✓' if readiness_valid else '✗'} readiness: {readiness_msg}")
    print(f"  {'✓' if monitoring_valid else '✗'} monitoring: {monitoring_msg}")
    
    # Write report
    report_path = Path("docs/audit/automated_release_validation_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport written to: {report_path}")
    
    # Exit code: 0 if all valid, 1 if any invalid
    return 0 if all_valid else 1


if __name__ == "__main__":
    try:
        exit_code = generate_validation_report()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
