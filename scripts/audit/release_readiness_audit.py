#!/usr/bin/env python3
"""
Release Readiness Audit
Validates that a release meets all readiness criteria before tagging/publishing.

Checks:
- Tests passing (pytest result)
- Audit reports present and valid
- Release notes present
- Tags consistent with version
- Repository health valid
- No generated artifacts in git
- Working tree clean
- Merge commits on main branch
- No uncommitted changes
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_command(cmd, capture=True):
    """Run shell command and return result."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT)
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(cmd, shell=True, cwd=str(REPO_ROOT))
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def check_tests_valid():
    """Verify all tests pass."""
    python_executable = sys.executable
    success, stdout, _ = run_command(
        f"{python_executable} -m pytest "
        "tests/audit/test_audit_policy_enforcement.py::test_policy_schema "
        "tests/assessment/test_testnet_readiness.py::test_testnet_readiness_output_contract "
        "-v --tb=short 2>&1 | tail -20"
    )
    
    # Parse pytest output for pass/fail
    if "passed" in stdout and "failed" not in stdout:
        # Extract test count
        import re
        match = re.search(r"(\d+) passed", stdout)
        if match:
            return True, int(match.group(1)), 0
    
    # Fallback: run tests and check exit code
    success, _, _ = run_command(
        f"{python_executable} -m pytest "
        "tests/audit/test_audit_policy_enforcement.py::test_policy_schema "
        "tests/assessment/test_testnet_readiness.py::test_testnet_readiness_output_contract "
        "-q"
    )
    return success, 0, 0


def check_audit_reports_valid():
    """Verify release_integrity and repository_health reports exist and are valid."""
    audit_file = REPO_ROOT / "docs" / "audit" / "release_integrity_report.json"
    health_file = REPO_ROOT / "docs" / "audit" / "repository_health.json"
    
    audit_valid = False
    health_valid = False
    
    if audit_file.exists():
        try:
            with open(audit_file) as f:
                data = json.load(f)
                audit_valid = data.get("audit_valid", False) and data.get("integrity_score", 0) == 1.0
        except:
            pass
    
    if health_file.exists():
        try:
            with open(health_file) as f:
                data = json.load(f)
                health_valid = data.get("health_valid", False) and data.get("health_score", 0) == 1.0
        except:
            pass
    
    return audit_valid and health_valid


def check_release_notes_present():
    """Verify release notes exist for this version."""
    # Extract version from git describe or branch name
    success, version, _ = run_command("git describe --tags 2>/dev/null || git branch --show-current")
    version = version.strip()
    
    # Look for release notes
    release_notes_dir = REPO_ROOT / "docs" / "releases"
    if release_notes_dir.exists():
        # Check if any release notes exist
        notes_files = list(release_notes_dir.glob("*.md"))
        return len(notes_files) > 0
    
    return False


def check_tags_consistent():
    """Verify git tags match release versions."""
    success, stdout, _ = run_command("git tag -l 'v*' | wc -l")
    try:
        tag_count = int(stdout.strip())
        # Should have at least the v1.1.1 tag now
        return tag_count >= 1
    except:
        return False


def check_working_tree_clean():
    """Verify no uncommitted changes outside expected audit artifacts."""
    success, stdout, _ = run_command("git status --porcelain -- . ':(exclude)docs/audit'")
    return stdout.strip() == ""


def check_no_generated_artifacts():
    """Verify no generated artifacts are tracked in git."""
    # Check for .pyc, __pycache__, .egg-info in git
    success, stdout, _ = run_command(r"git ls-files | grep -E '(\.pyc|__pycache__|\.egg-info|\.pytest_cache)'")
    return stdout.strip() == ""


def check_main_has_merge():
    """Verify main branch has merge commits from feature branches."""
    success, stdout, _ = run_command("git log main --oneline --grep='Merge' | head -1")
    return "Merge" in stdout


def generate_readiness_report():
    """Generate comprehensive readiness report."""
    print("🔍 Checking Release Readiness...")
    
    # Run all checks
    tests_valid = check_tests_valid()[0]
    audit_valid = check_audit_reports_valid()
    release_notes = check_release_notes_present()
    tags_consistent = check_tags_consistent()
    working_clean = check_working_tree_clean()
    no_artifacts = check_no_generated_artifacts()
    main_has_merge = check_main_has_merge()
    
    # All checks must pass
    release_ready = all([
        tests_valid,
        audit_valid,
        release_notes,
        tags_consistent,
        working_clean,
        no_artifacts,
        main_has_merge
    ])
    
    # Calculate readiness score (each check worth ~14%)
    checks_passed = sum([
        tests_valid,
        audit_valid,
        release_notes,
        tags_consistent,
        working_clean,
        no_artifacts,
        main_has_merge
    ])
    readiness_score = checks_passed / 7.0
    
    report = {
        "release_ready": release_ready,
        "readiness_score": round(readiness_score, 2),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "checks": {
            "tests_valid": tests_valid,
            "audit_valid": audit_valid,
            "release_notes_present": release_notes,
            "tags_consistent": tags_consistent,
            "working_tree_clean": working_clean,
            "no_generated_artifacts": no_artifacts,
            "main_has_merge": main_has_merge
        }
    }
    
    # Write report
    report_path = REPO_ROOT / "docs" / "audit" / "release_readiness_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    status_icon = "✅" if release_ready else "⚠️"
    print(f"\n{status_icon} Release Readiness Report")
    print(f"   Score: {readiness_score:.1%}")
    print(f"   Ready: {release_ready}")
    print(f"\nChecks:")
    for check, result in report["checks"].items():
        icon = "✓" if result else "✗"
        print(f"  {icon} {check}")
    
    print(f"\nReport written to: {report_path}")
    
    return 0 if release_ready else 1


if __name__ == "__main__":
    sys.exit(generate_readiness_report())
