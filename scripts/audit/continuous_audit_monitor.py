#!/usr/bin/env python3
"""
Continuous Audit Monitor
Tracks audit drift over time by comparing current state against baseline reports.

Detects:
- Integrity drift (tags, releases, version consistency)
- Health drift (test count, audit count, branch/tag changes)
- Readiness drift (failing checks, lowered scores)
- Monitoring drift (failed monitoring operations)

Generates monitoring report with drift detection.
"""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_command(cmd):
    """Run shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def load_report(report_path):
    """Load and parse a report JSON file."""
    try:
        with open(report_path) as f:
            return json.load(f)
    except:
        return None


def check_integrity_drift():
    """Check for drift in integrity metrics."""
    report_path = REPO_ROOT / "docs" / "audit" / "release_integrity_report.json"
    
    if not report_path.exists():
        return False, "Report missing"
    
    report = load_report(report_path)
    if not report:
        return False, "Invalid JSON"
    
    tags_checked = report.get("tags_checked", 0)
    tags_valid = report.get("tags_valid", 0)
    integrity_score = report.get("integrity_score", 0)
    audit_valid = report.get("audit_valid", False)
    
    drift = (
        integrity_score != 1.0 or
        not audit_valid or
        tags_checked != tags_valid
    )
    
    return not drift, ("Integrity OK" if not drift else "Integrity drift detected")


def check_health_drift():
    """Check for drift in health metrics."""
    report_path = REPO_ROOT / "docs" / "audit" / "repository_health.json"
    
    if not report_path.exists():
        return False, "Report missing"
    
    report = load_report(report_path)
    if not report:
        return False, "Invalid JSON"
    
    # Current baseline metrics
    expected_health_valid = True
    expected_health_score = 1.0
    expected_audit_count = 7
    expected_test_count = 26
    expected_tag_count = 35
    
    health_valid = report.get("health_valid", False)
    health_score = report.get("health_score", 0)
    audit_count = report.get("audit_count", 0)
    test_count = report.get("test_count", 0)
    tag_count = report.get("tag_count", 0)
    
    drift = (
        health_valid != expected_health_valid or
        health_score != expected_health_score or
        audit_count < expected_audit_count or  # Can increase but not decrease
        test_count < expected_test_count or
        tag_count < expected_tag_count
    )
    
    return not drift, ("Health OK" if not drift else "Health drift detected")


def check_readiness_drift():
    """Check for drift in readiness metrics."""
    report_path = REPO_ROOT / "docs" / "audit" / "release_readiness_report.json"
    
    if not report_path.exists():
        return False, "Report missing"
    
    report = load_report(report_path)
    if not report:
        return False, "Invalid JSON"
    
    # Current baseline: all checks passing, score 1.0
    expected_ready = True
    expected_score = 1.0
    expected_checks_count = 7
    
    release_ready = report.get("release_ready", False)
    readiness_score = report.get("readiness_score", 0)
    checks = report.get("checks", {})
    
    # All checks should still pass
    all_checks_pass = all(checks.values()) if checks else False
    
    drift = (
        release_ready != expected_ready or
        readiness_score != expected_score or
        not all_checks_pass or
        len(checks) != expected_checks_count
    )
    
    return not drift, ("Readiness OK" if not drift else "Readiness drift detected")


def check_working_tree_clean():
    """Verify working tree hasn't degraded."""
    success, stdout, _ = run_command("git status --porcelain -- . ':(exclude)docs/audit'")
    
    if success and stdout.strip() == "":
        return True, "Working tree clean"
    else:
        return False, "Working tree has uncommitted changes"


def generate_monitoring_report():
    """Generate comprehensive monitoring report."""
    print("📊 Continuous Audit Monitor")
    
    # Run all drift checks
    integrity_ok, integrity_msg = check_integrity_drift()
    health_ok, health_msg = check_health_drift()
    readiness_ok, readiness_msg = check_readiness_drift()
    tree_clean, tree_msg = check_working_tree_clean()
    
    # Determine overall monitoring state
    monitoring_valid = all([integrity_ok, health_ok, readiness_ok, tree_clean])
    
    # Calculate monitoring score (weighted)
    checks_pass = sum([integrity_ok, health_ok, readiness_ok, tree_clean])
    monitoring_score = checks_pass / 4.0
    
    report = {
        "monitoring_valid": monitoring_valid,
        "monitoring_score": round(monitoring_score, 2),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "drift_detection": {
            "audit_drift_detected": not integrity_ok,
            "health_drift_detected": not health_ok,
            "readiness_drift_detected": not readiness_ok,
            "working_tree_drift_detected": not tree_clean
        },
        "checks": {
            "integrity": {"valid": integrity_ok, "message": integrity_msg},
            "health": {"valid": health_ok, "message": health_msg},
            "readiness": {"valid": readiness_ok, "message": readiness_msg},
            "working_tree": {"valid": tree_clean, "message": tree_msg}
        }
    }
    
    # Write report
    report_path = REPO_ROOT / "docs" / "audit" / "continuous_audit_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    status_icon = "✅" if monitoring_valid else "⚠️"
    print(f"\n{status_icon} Continuous Audit Monitoring")
    print(f"   Score: {monitoring_score:.0%}")
    print(f"   Valid: {monitoring_valid}")
    print(f"\nDrift Detection:")
    for drift_type, detected in report["drift_detection"].items():
        icon = "🔴" if detected else "✓"
        print(f"  {icon} {drift_type}: {detected}")
    print(f"\nDetailed Checks:")
    for check_name, check_result in report["checks"].items():
        icon = "✓" if check_result["valid"] else "✗"
        print(f"  {icon} {check_name}: {check_result['message']}")
    
    print(f"\nReport written to: {report_path}")
    
    return 0 if monitoring_valid else 1


if __name__ == "__main__":
    import sys
    sys.exit(generate_monitoring_report())
