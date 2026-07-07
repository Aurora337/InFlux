#!/usr/bin/env python3
"""
Test suite for Automated Release Validation (v1.1.4)

Tests validate:
- Script structure and executability
- JSON report generation
- Report schema validation
- Validation logic consistency
- Overall release approval determination
"""

import json
import subprocess
from pathlib import Path

import pytest

from runtime_executable import PYTHON_EXECUTABLE


class TestAutomatedReleaseValidation:
    """Test suite for automated release validation script."""

    @pytest.fixture
    def script_path(self):
        """Return path to validation script."""
        return Path("scripts/audit/automated_release_validation.py")

    @pytest.fixture
    def report_path(self):
        """Return path to validation report."""
        return Path("docs/audit/automated_release_validation_report.json")

    def test_validation_script_exists(self, script_path):
        """Verify validation script exists."""
        assert script_path.exists(), f"Script not found: {script_path}"

    def test_validation_script_executable(self, script_path):
        """Verify validation script runs without error."""
        result = subprocess.run(
            [PYTHON_EXECUTABLE, str(script_path)],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        # Script should exit with 0 (valid) or 1 (invalid), not error
        assert result.returncode in [0, 1], f"Script failed: {result.stderr}"

    def test_validation_report_generated(self, report_path):
        """Verify validation report is generated."""
        # Run script to generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        assert report_path.exists(), f"Report not generated: {report_path}"

    def test_validation_report_valid_json(self, report_path):
        """Verify report is valid JSON."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict), "Report is not a JSON object"

    def test_validation_report_has_required_fields(self, report_path):
        """Verify report contains all required fields."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        required_fields = [
            "validation_valid",
            "validation_score",
            "release_integrity_valid",
            "repository_health_valid",
            "release_readiness_valid",
            "continuous_monitoring_valid",
            "release_approved",
            "checks",
            "timestamp"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_validation_checks_structure(self, report_path):
        """Verify checks have required structure."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        checks = data.get("checks", {})
        required_checks = ["integrity", "health", "readiness", "monitoring"]
        
        for check_name in required_checks:
            assert check_name in checks, f"Missing check: {check_name}"
            
            check = checks[check_name]
            assert isinstance(check.get("valid"), bool), f"Check {check_name} missing valid bool"
            assert isinstance(check.get("message"), str), f"Check {check_name} missing message"

    def test_validation_score_valid_range(self, report_path):
        """Verify validation score is between 0 and 1."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        score = data.get("validation_score", -1)
        assert 0 <= score <= 1, f"Score out of range: {score}"

    def test_validation_valid_consistency(self, report_path):
        """Verify validation_valid matches overall result."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        # validation_valid should be true only if all checks pass
        validation_valid = data.get("validation_valid")
        checks = data.get("checks", {})
        
        all_checks_pass = all(
            check.get("valid", False)
            for check in checks.values()
        )
        
        assert validation_valid == all_checks_pass, \
            "validation_valid does not match check results"

    def test_release_approved_matches_validation_valid(self, report_path):
        """Verify release_approved matches validation_valid."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        validation_valid = data.get("validation_valid")
        release_approved = data.get("release_approved")
        
        assert validation_valid == release_approved, \
            "release_approved should match validation_valid"

    def test_report_has_timestamp(self, report_path):
        """Verify report includes RFC3339 timestamp."""
        # Generate report
        subprocess.run(
            [PYTHON_EXECUTABLE, "scripts/audit/automated_release_validation.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        timestamp = data.get("timestamp")
        assert timestamp, "Missing timestamp"
        assert timestamp.endswith("Z"), "Timestamp should end with Z (UTC)"
