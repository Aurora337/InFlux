"""
Unit tests for the drift detector module.

Tests configuration drift detection, state divergence detection,
policy violations, specification drift, consensus drift,
severity/category filtering, and snapshot behavior.
"""


from influx.governance.drift_detector import (
    DriftDetector,
    DriftEvent,
    DriftSeverity,
    DriftCategory,
)


class TestDriftDetectorInit:
    """Drift detector initialization tests."""

    def test_initialization(self):
        """DriftDetector should initialize with empty events."""
        detector = DriftDetector()
        assert detector.events == []
        assert detector.detection_count == 0
        assert detector.last_check_time is not None


class TestConfigDrift:
    """Configuration drift detection tests."""

    def test_config_drift_detected(self):
        """Different expected/actual values should create a drift event."""
        detector = DriftDetector()
        event = detector.detect_config_drift(
            component="consensus.timeout",
            expected=1000,
            actual=2000,
            message="Timeout drifted",
            severity=DriftSeverity.WARNING,
        )
        assert event is not None
        assert event.category == DriftCategory.CONFIG
        assert event.severity == DriftSeverity.WARNING
        assert event.component == "consensus.timeout"
        assert event.expected == 1000
        assert event.actual == 2000
        assert detector.detection_count == 1
        assert len(detector.events) == 1

    def test_config_drift_no_drift(self):
        """Same expected/actual values should not create a drift event."""
        detector = DriftDetector()
        event = detector.detect_config_drift(
            component="consensus.timeout",
            expected=1000,
            actual=1000,
            message="No drift",
        )
        assert event is None
        assert detector.detection_count == 0

    def test_config_drift_default_severity(self):
        """Default severity for config drift should be WARNING."""
        detector = DriftDetector()
        event = detector.detect_config_drift(
            component="test.param",
            expected="old",
            actual="new",
            message="Param drifted",
        )
        assert event.severity == DriftSeverity.WARNING

    def test_config_drift_critical(self):
        """Config drift can be set to CRITICAL severity."""
        detector = DriftDetector()
        event = detector.detect_config_drift(
            component="security.threshold",
            expected=100,
            actual=0,
            message="Security threshold disabled!",
            severity=DriftSeverity.CRITICAL,
        )
        assert event.severity == DriftSeverity.CRITICAL


class TestStateDivergence:
    """State divergence detection tests."""

    def test_state_divergence_detected(self):
        """Different state values should create a divergence event."""
        detector = DriftDetector()
        event = detector.detect_state_divergence(
            component="validator.state",
            expected_state="active",
            actual_state="jailed",
            message="Validator state mismatch",
        )
        assert event is not None
        assert event.category == DriftCategory.STATE
        assert event.severity == DriftSeverity.CRITICAL

    def test_state_divergence_no_divergence(self):
        """Same state values should not create an event."""
        detector = DriftDetector()
        event = detector.detect_state_divergence(
            component="validator.state",
            expected_state="active",
            actual_state="active",
            message="No divergence",
        )
        assert event is None

    def test_state_divergence_complex_types(self):
        """State divergence should work with complex types (dicts)."""
        detector = DriftDetector()
        expected = {"balance": 1000, "status": "active"}
        actual = {"balance": 500, "status": "jailed"}
        event = detector.detect_state_divergence(
            component="account",
            expected_state=expected,
            actual_state=actual,
            message="Account state diverged",
        )
        assert event is not None


class TestPolicyViolation:
    """Policy violation detection tests."""

    def test_policy_violation_created(self):
        """Policy violation should always create an event."""
        detector = DriftDetector()
        event = detector.detect_policy_violation(
            component="staking",
            policy="min_self_delegation >= 1000",
            violation="validator has 0 self-delegation",
        )
        assert event is not None
        assert event.category == DriftCategory.POLICY
        assert event.severity == DriftSeverity.CRITICAL
        assert "Policy violation" in event.message

    def test_policy_violation_custom_severity(self):
        """Policy violation can have custom severity."""
        detector = DriftDetector()
        event = detector.detect_policy_violation(
            component="governance",
            policy="quorum >= 0.4",
            violation="quorum set to 0.1",
            severity=DriftSeverity.WARNING,
        )
        assert event.severity == DriftSeverity.WARNING


class TestSpecificationDrift:
    """Specification drift detection tests."""

    def test_spec_drift_created(self):
        """Spec drift should always create an event."""
        detector = DriftDetector()
        event = detector.detect_specification_drift(
            spec_source="whitepaper.md",
            spec_statement="Voting period is 7 days",
            implementation="Voting period is 3 days",
            message="Voting period does not match whitepaper",
        )
        assert event is not None
        assert event.category == DriftCategory.SPECIFICATION
        assert event.severity == DriftSeverity.WARNING

    def test_spec_drift_multiple(self):
        """Multiple spec drifts should each create an event."""
        detector = DriftDetector()
        detector.detect_specification_drift(
            spec_source="arch.md", spec_statement="A", implementation="B",
            message="Drift 1", severity=DriftSeverity.WARNING,
        )
        detector.detect_specification_drift(
            spec_source="arch.md", spec_statement="C", implementation="D",
            message="Drift 2", severity=DriftSeverity.CRITICAL,
        )
        assert detector.detection_count == 2
        assert len(detector.events) == 2


class TestConsensusDrift:
    """Consensus parameter drift detection tests."""

    def test_consensus_drift_detected(self):
        """Differences in consensus params should create events."""
        detector = DriftDetector()
        expected = {"timeout": 1000, "rounds": 10, "threshold": 0.66}
        actual = {"timeout": 2000, "rounds": 10, "threshold": 0.5}

        events = detector.detect_consensus_drift(expected, actual)
        assert len(events) == 2  # timeout and threshold drifted

    def test_consensus_drift_no_drift(self):
        """Same consensus params should not create events."""
        detector = DriftDetector()
        params = {"timeout": 1000, "rounds": 10, "threshold": 0.66}
        events = detector.detect_consensus_drift(params, params)
        assert len(events) == 0


class TestEventFiltering:
    """Drift event filtering tests."""

    def test_filter_by_severity(self):
        """Events should be filterable by severity."""
        detector = DriftDetector()
        detector.detect_config_drift("a", 1, 2, "info", DriftSeverity.INFO)
        detector.detect_config_drift("b", 1, 2, "warning", DriftSeverity.WARNING)
        detector.detect_config_drift("c", 1, 2, "critical", DriftSeverity.CRITICAL)

        info_events = detector.get_events_by_severity(DriftSeverity.INFO)
        warning_events = detector.get_events_by_severity(DriftSeverity.WARNING)
        critical_events = detector.get_events_by_severity(DriftSeverity.CRITICAL)

        assert len(info_events) == 1
        assert len(warning_events) == 1
        assert len(critical_events) == 1

    def test_filter_by_category(self):
        """Events should be filterable by category."""
        detector = DriftDetector()
        detector.detect_config_drift("a", 1, 2, "config drift")
        detector.detect_policy_violation("b", "policy x", "violation y")

        config_events = detector.get_events_by_category(DriftCategory.CONFIG)
        policy_events = detector.get_events_by_category(DriftCategory.POLICY)

        assert len(config_events) == 1
        assert len(policy_events) == 1

    def test_has_critical_drift(self):
        """has_critical_drift should detect CRITICAL events."""
        detector = DriftDetector()
        assert detector.has_critical_drift() is False

        detector.detect_config_drift("a", 1, 2, "warning", DriftSeverity.WARNING)
        assert detector.has_critical_drift() is False

        detector.detect_config_drift("b", 1, 0, "critical", DriftSeverity.CRITICAL)
        assert detector.has_critical_drift() is True


class TestDriftSnapshot:
    """Drift detector snapshot tests."""

    def test_snapshot_empty(self):
        """Empty detector snapshot should reflect zero state."""
        detector = DriftDetector()
        snap = detector.snapshot()
        assert snap["detection_count"] == 0
        assert snap["event_count"] == 0
        assert snap["critical_events"] == 0
        assert snap["warning_events"] == 0
        assert snap["info_events"] == 0
        assert snap["recent_events"] == []

    def test_snapshot_with_events(self):
        """Snapshot should reflect recorded events."""
        detector = DriftDetector()
        detector.detect_config_drift("a", 1, 2, "warning", DriftSeverity.WARNING)
        detector.detect_state_divergence("b", "x", "y", "critical")

        snap = detector.snapshot()
        assert snap["detection_count"] == 2
        assert snap["event_count"] == 2
        assert snap["warning_events"] == 1
        assert snap["critical_events"] == 1
        assert len(snap["recent_events"]) == 2

    def test_check_all(self):
        """check_all should return all events and update last_check_time."""
        detector = DriftDetector()
        detector.detect_config_drift("a", 1, 2, "drift")
        original_time = detector.last_check_time

        events = detector.check_all()
        assert len(events) == 1
        assert detector.last_check_time >= original_time


class TestDriftEvent:
    """DriftEvent creation and snapshot tests."""

    def test_event_snapshot(self):
        """DriftEvent snapshot should contain all fields."""
        event = DriftEvent(
            event_id="evt-001",
            category=DriftCategory.CONFIG,
            severity=DriftSeverity.CRITICAL,
            component="test.component",
            expected=100,
            actual=0,
            message="Critical parameter mismatch",
        )
        snap = event.snapshot()
        assert snap["event_id"] == "evt-001"
        assert snap["category"] == "config"
        assert snap["severity"] == "critical"
        assert snap["component"] == "test.component"
        assert snap["expected"] == "100"
        assert snap["actual"] == "0"
        assert snap["message"] == "Critical parameter mismatch"
        assert snap["timestamp"] > 0
