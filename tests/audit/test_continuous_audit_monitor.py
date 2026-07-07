"""
Test Continuous Audit Monitor Script
Validates continuous_audit_monitor.py functionality and drift detection
"""

import json
import subprocess
from pathlib import Path

import pytest

from runtime_executable import PYTHON_EXECUTABLE


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestContinuousAuditMonitor:
    """Tests for continuous audit monitor."""
    
    @pytest.fixture
    def monitor_script(self):
        """Path to monitor script."""
        return REPO_ROOT / "scripts" / "audit" / "continuous_audit_monitor.py"
    
    @pytest.fixture
    def report_file(self):
        """Path to generated report."""
        return REPO_ROOT / "docs" / "audit" / "continuous_audit_report.json"
    
    def test_monitor_script_exists(self, monitor_script):
        """Verify monitor script is present."""
        assert monitor_script.exists(), "continuous_audit_monitor.py not found"
    
    def test_monitor_script_executable(self, monitor_script):
        """Verify script runs without errors."""
        result = subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        assert result.returncode in [0, 1], f"Script failed: {result.stderr}"
    
    def test_report_generated(self, monitor_script, report_file):
        """Verify report JSON is generated."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        assert report_file.exists(), "Report JSON not generated"
    
    def test_report_valid_json(self, monitor_script, report_file):
        """Verify report is valid JSON."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        assert isinstance(data, dict), "Report should be JSON object"
    
    def test_report_has_required_fields(self, monitor_script, report_file):
        """Verify report has all required fields."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        required_fields = [
            "monitoring_valid",
            "monitoring_score",
            "timestamp",
            "drift_detection",
            "checks"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_drift_detection_structure(self, monitor_script, report_file):
        """Verify drift_detection object has expected structure."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        expected_drifts = [
            "audit_drift_detected",
            "health_drift_detected",
            "readiness_drift_detected",
            "working_tree_drift_detected"
        ]
        
        drifts = data.get("drift_detection", {})
        for drift in expected_drifts:
            assert drift in drifts, f"Missing drift type: {drift}"
            assert isinstance(drifts[drift], bool), f"{drift} should be boolean"
    
    def test_checks_structure(self, monitor_script, report_file):
        """Verify checks object has expected structure."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        expected_checks = [
            "integrity",
            "health",
            "readiness",
            "working_tree"
        ]
        
        checks = data.get("checks", {})
        for check in expected_checks:
            assert check in checks, f"Missing check: {check}"
            assert "valid" in checks[check], f"{check} missing 'valid' field"
            assert "message" in checks[check], f"{check} missing 'message' field"
            assert isinstance(checks[check]["valid"], bool), f"{check}.valid should be boolean"
    
    def test_monitoring_score_valid_range(self, monitor_script, report_file):
        """Verify monitoring score is between 0 and 1."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        score = data.get("monitoring_score", -1)
        assert 0 <= score <= 1, f"Score out of range: {score}"
    
    def test_monitoring_valid_consistency(self, monitor_script, report_file):
        """Verify monitoring_valid matches no drifts detected."""
        subprocess.run(
            [PYTHON_EXECUTABLE, str(monitor_script)],
            capture_output=True,
            cwd=str(REPO_ROOT)
        )
        
        with open(report_file) as f:
            data = json.load(f)
        
        monitoring_valid = data.get("monitoring_valid", False)
        drifts = data.get("drift_detection", {})
        no_drifts = not any(drifts.values()) if drifts else False
        
        assert monitoring_valid == no_drifts, \
            "monitoring_valid should be true when no drifts detected"
