"""
Specification drift detection for InFlux governance.

Monitors configuration drift, state divergence, policy violations,
and specification alignment across the protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class DriftSeverity(Enum):
    """Severity levels for detected drift."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DriftCategory(Enum):
    """Categories of detectable drift."""

    CONFIG = "config"
    STATE = "state"
    POLICY = "policy"
    SPECIFICATION = "specification"
    CONSENSUS = "consensus"
    GOVERNANCE = "governance"


@dataclass(slots=True)
class DriftEvent:
    """
    A single drift detection event.

    Captures what drifted, the expected vs actual values,
    severity, and timestamp for audit trail.
    """

    event_id: str
    category: DriftCategory
    severity: DriftSeverity
    component: str
    expected: Any
    actual: Any
    message: str
    timestamp: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))

    def snapshot(self) -> dict[str, Any]:
        """Deterministic drift event snapshot."""
        return {
            "event_id": self.event_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "component": self.component,
            "expected": str(self.expected),
            "actual": str(self.actual),
            "message": self.message,
            "timestamp": self.timestamp,
        }


@dataclass(slots=True)
class DriftDetector:
    """
    Detects and reports specification and configuration drift.

    Monitors:
    - Configuration drift across nodes
    - State divergence between expected and actual
    - Policy violations
    - Specification alignment (whitepaper, architecture, economics, governance)
    - Consensus parameter drift
    - Governance parameter drift
    """

    events: list[DriftEvent] = field(default_factory=list)
    detection_count: int = 0
    last_check_time: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))

    def _generate_event_id(self) -> str:
        """Generate a deterministic event ID."""
        import hashlib
        raw = f"drift-{self.detection_count}-{datetime.now(timezone.utc).timestamp()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def detect_config_drift(self, component: str, expected: Any, actual: Any,
                             message: str, severity: DriftSeverity = DriftSeverity.WARNING) -> Optional[DriftEvent]:
        """
        Detect configuration drift between expected and actual values.

        Args:
            component: The component being checked
            expected: The expected configuration value
            actual: The actual configuration value
            message: Human-readable drift description
            severity: Severity level of the drift

        Returns:
            The created DriftEvent, or None if no drift
        """
        if expected == actual:
            # No drift detected
            return None

        event = DriftEvent(
            event_id=self._generate_event_id(),
            category=DriftCategory.CONFIG,
            severity=severity,
            component=component,
            expected=expected,
            actual=actual,
            message=message,
        )
        self.events.append(event)
        self.detection_count += 1
        return event

    def detect_state_divergence(self, component: str, expected_state: Any,
                                  actual_state: Any, message: str,
                                  severity: DriftSeverity = DriftSeverity.CRITICAL) -> Optional[DriftEvent]:
        """
        Detect state divergence between expected and actual state.

        Args:
            component: The component being checked
            expected_state: The expected state
            actual_state: The actual state
            message: Human-readable divergence description
            severity: Severity level

        Returns:
            The created DriftEvent, or None if no divergence
        """
        if expected_state == actual_state:
            return None

        event = DriftEvent(
            event_id=self._generate_event_id(),
            category=DriftCategory.STATE,
            severity=severity,
            component=component,
            expected=expected_state,
            actual=actual_state,
            message=message,
        )
        self.events.append(event)
        self.detection_count += 1
        return event

    def detect_policy_violation(self, component: str, policy: str,
                                  violation: str,
                                  severity: DriftSeverity = DriftSeverity.CRITICAL) -> DriftEvent:
        """
        Detect a policy violation.

        Args:
            component: The component where the violation occurred
            policy: The policy that was violated
            violation: Description of the violation
            severity: Severity level

        Returns:
            The created DriftEvent
        """
        event = DriftEvent(
            event_id=self._generate_event_id(),
            category=DriftCategory.POLICY,
            severity=severity,
            component=component,
            expected=policy,
            actual=violation,
            message=f"Policy violation: {policy} - {violation}",
        )
        self.events.append(event)
        self.detection_count += 1
        return event

    def detect_specification_drift(self, spec_source: str, spec_statement: str,
                                     implementation: str, message: str,
                                     severity: DriftSeverity = DriftSeverity.WARNING) -> DriftEvent:
        """
        Detect drift between specification and implementation.

        Args:
            spec_source: The specification document/source
            spec_statement: The specification statement being checked
            implementation: The actual implementation behavior
            message: Human-readable drift description
            severity: Severity level

        Returns:
            The created DriftEvent
        """
        event = DriftEvent(
            event_id=self._generate_event_id(),
            category=DriftCategory.SPECIFICATION,
            severity=severity,
            component=spec_source,
            expected=spec_statement,
            actual=implementation,
            message=message,
        )
        self.events.append(event)
        self.detection_count += 1
        return event

    def detect_consensus_drift(self, expected_consensus: dict[str, Any],
                                 actual_consensus: dict[str, Any],
                                 severity: DriftSeverity = DriftSeverity.CRITICAL) -> list[DriftEvent]:
        """
        Detect drift between expected and actual consensus parameters.

        Args:
            expected_consensus: Expected consensus parameters
            actual_consensus: Actual consensus parameters
            severity: Severity level

        Returns:
            List of DriftEvents for each parameter that drifted
        """
        events = []
        all_keys = set(expected_consensus.keys()) | set(actual_consensus.keys())
        for key in all_keys:
            expected = expected_consensus.get(key)
            actual = actual_consensus.get(key)
            if expected != actual:
                event = self.detect_config_drift(
                    component=f"consensus.{key}",
                    expected=expected,
                    actual=actual,
                    message=f"Consensus parameter '{key}' drifted: expected {expected}, got {actual}",
                    severity=severity,
                )
                if event:
                    events.append(event)
        return events

    def check_all(self, state_snapshot: Optional[dict[str, Any]] = None) -> list[DriftEvent]:
        """
        Run all drift detection checks.

        Args:
            state_snapshot: Optional current state snapshot to check against expected

        Returns:
            List of all drift events found
        """
        self.last_check_time = int(datetime.now(timezone.utc).timestamp())
        return list(self.events)

    def get_events_by_severity(self, severity: DriftSeverity) -> list[DriftEvent]:
        """Filter drift events by severity level."""
        return [e for e in self.events if e.severity == severity]

    def get_events_by_category(self, category: DriftCategory) -> list[DriftEvent]:
        """Filter drift events by category."""
        return [e for e in self.events if e.category == category]

    def has_critical_drift(self) -> bool:
        """Check if any critical drift events exist."""
        return any(e.severity == DriftSeverity.CRITICAL for e in self.events)

    def snapshot(self) -> dict[str, Any]:
        """Deterministic drift detector snapshot."""
        return {
            "detection_count": self.detection_count,
            "event_count": len(self.events),
            "last_check_time": self.last_check_time,
            "critical_events": sum(1 for e in self.events if e.severity == DriftSeverity.CRITICAL),
            "warning_events": sum(1 for e in self.events if e.severity == DriftSeverity.WARNING),
            "info_events": sum(1 for e in self.events if e.severity == DriftSeverity.INFO),
            "recent_events": [e.snapshot() for e in self.events[-10:]],
        }
