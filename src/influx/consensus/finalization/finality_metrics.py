from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FinalityMetrics:
    """
    Tracks deterministic finalization activity.
    """

    certificates_created: int = 0

    blocks_finalized: int = 0

    quorum_failures: int = 0

    validation_failures: int = 0

    average_finalization_time: float = 0.0

    def record_certificate(
        self,
    ) -> None:
        self.certificates_created += 1

    def record_finalization(
        self,
    ) -> None:
        self.blocks_finalized += 1

    def record_quorum_failure(
        self,
    ) -> None:
        self.quorum_failures += 1

    def record_validation_failure(
        self,
    ) -> None:
        self.validation_failures += 1

    def update_finalization_time(
        self,
        seconds: float,
    ) -> None:
        """
        Rolling deterministic average.
        """

        if self.average_finalization_time == 0.0:
            self.average_finalization_time = seconds
            return

        self.average_finalization_time = (
            self.average_finalization_time + seconds
        ) / 2.0

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "certificates_created":
                self.certificates_created,

            "blocks_finalized":
                self.blocks_finalized,

            "quorum_failures":
                self.quorum_failures,

            "validation_failures":
                self.validation_failures,

            "average_finalization_time":
                self.average_finalization_time,
        }