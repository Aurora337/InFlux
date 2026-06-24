"""
Test Release Readiness Audit Script
Validates the release_readiness_audit.py functionality
"""

import json
import subprocess
from pathlib import Path

import pytest

from runtime_executable import PYTHON_EXECUTABLE


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestReleaseReadinessAudit:
    """Tests for release readiness audit checks."""
    
    @pytest.fixture
    def audit_script(self):
        """Path to audit script."""
        return REPO_ROOT / "scripts" / "audit" / "release_readiness_audit.py"
    
    @pytest.fixture
    def report_file(self):
        """Path to generated report."""
        return REPO_ROOT / "docs" / "audit" / "release_readiness_report.json"
    
    def test_audit_script_exists(self, audit_script):
        """Verify audit script is present."""
        assert audit_script.exists(), "release_readiness_audit.py not found"
    
    def test_audit_script_executable(self, audit_script):
        """Verify script runs without errors."""
        result = subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        assert result.returncode in [0, 1], f"Script failed: {result.stderr}"
    
    def test_report_generated(self, audit_script, report_file):
        """Verify report JSON is generated."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        assert report_file.exists(), "Report JSON not generated"
    
    def test_report_valid_json(self, audit_script, report_file):
        """Verify report is valid JSON."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        assert isinstance(data, dict), "Report should be JSON object"
    
    def test_report_has_required_fields(self, audit_script, report_file):
        """Verify report has all required fields."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        required_fields = [
            "release_ready",
            "readiness_score",
            "timestamp",
            "checks"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_report_checks_structure(self, audit_script, report_file):
        """Verify checks object has expected structure."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        expected_checks = [
            "tests_valid",
            "audit_valid",
            "release_notes_present",
            "tags_consistent",
            "working_tree_clean",
            "no_generated_artifacts",
            "main_has_merge"
        ]
        
        checks = data.get("checks", {})
        for check in expected_checks:
            assert check in checks, f"Missing check: {check}"
            assert isinstance(checks[check], bool), f"{check} should be boolean"
    
    def test_readiness_score_valid_range(self, audit_script, report_file):
        """Verify readiness score is between 0 and 1."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        score = data.get("readiness_score", -1)
        assert 0 <= score <= 1, f"Score out of range: {score}"
    
    def test_release_ready_consistency(self, audit_script, report_file):
        """Verify release_ready matches all checks passing."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(audit_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        release_ready = data.get("release_ready", False)
        all_checks = all(data.get("checks", {}).values())
        
        assert release_ready == all_checks, \
            "release_ready should match whether all checks pass"
