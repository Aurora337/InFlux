from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReputationMetrics:
    """
    Tracks validator reputation activity.
    """

    faults_detected: int = 0

    penalties_applied: int = 0

    recoveries_started: int = 0

    recoveries_completed: int = 0

    score_updates: int = 0

    def record_fault(
        self,
    ) -> None:
        """
        Record detected fault.
        """

        self.faults_detected += 1

    def record_penalty(
        self,
    ) -> None:
        """
        Record applied penalty.
        """

        self.penalties_applied += 1

    def record_recovery_start(
        self,
    ) -> None:
        """
        Record recovery start.
        """

        self.recoveries_started += 1

    def record_recovery_complete(
        self,
    ) -> None:
        """
        Record completed recovery.
        """

        self.recoveries_completed += 1

    def record_score_update(
        self,
    ) -> None:
        """
        Record score modification.
        """

        self.score_updates += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "faults_detected":
                self.faults_detected,

            "penalties_applied":
                self.penalties_applied,

            "recoveries_started":
                self.recoveries_started,

            "recoveries_completed":
                self.recoveries_completed,

            "score_updates":
                self.score_updates,
        }