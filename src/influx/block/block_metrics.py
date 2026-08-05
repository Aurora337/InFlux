from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BlockMetrics:
    """
    Tracks deterministic block activity.
    """

    blocks_created: int = 0

    blocks_validated: int = 0

    blocks_rejected: int = 0

    blocks_committed: int = 0

    transactions_included: int = 0

    validation_failures: int = 0

    average_build_time: float = 0.0

    def record_created(
        self,
    ) -> None:
        self.blocks_created += 1

    def record_validated(
        self,
    ) -> None:
        self.blocks_validated += 1

    def record_rejected(
        self,
    ) -> None:
        self.blocks_rejected += 1

    def record_committed(
        self,
    ) -> None:
        self.blocks_committed += 1

    def record_transactions(
        self,
        count: int,
    ) -> None:
        self.transactions_included += count

    def record_validation_failure(
        self,
    ) -> None:
        self.validation_failures += 1

    def update_build_time(
        self,
        seconds: float,
    ) -> None:
        """
        Rolling average build time.
        """

        if self.average_build_time == 0.0:
            self.average_build_time = seconds
            return

        self.average_build_time = (
            self.average_build_time + seconds
        ) / 2.0

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "blocks_created":
                self.blocks_created,

            "blocks_validated":
                self.blocks_validated,

            "blocks_rejected":
                self.blocks_rejected,

            "blocks_committed":
                self.blocks_committed,

            "transactions_included":
                self.transactions_included,

            "validation_failures":
                self.validation_failures,

            "average_build_time":
                self.average_build_time,
        }