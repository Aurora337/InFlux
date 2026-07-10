from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LedgerMetrics:
    """
    Tracks deterministic ledger activity.
    """

    blocks_committed: int = 0

    transactions_applied: int = 0

    state_updates: int = 0

    validation_failures: int = 0

    commit_failures: int = 0

    average_commit_time: float = 0.0

    def record_block_commit(
        self,
    ) -> None:
        self.blocks_committed += 1

    def record_transaction(
        self,
        count: int = 1,
    ) -> None:
        self.transactions_applied += count

    def record_state_update(
        self,
    ) -> None:
        self.state_updates += 1

    def record_validation_failure(
        self,
    ) -> None:
        self.validation_failures += 1

    def record_commit_failure(
        self,
    ) -> None:
        self.commit_failures += 1

    def update_commit_time(
        self,
        seconds: float,
    ) -> None:

        if self.average_commit_time == 0.0:
            self.average_commit_time = seconds
            return

        self.average_commit_time = (
            self.average_commit_time + seconds
        ) / 2.0

    def snapshot(
        self,
    ) -> dict:

        return {
            "blocks_committed":
                self.blocks_committed,

            "transactions_applied":
                self.transactions_applied,

            "state_updates":
                self.state_updates,

            "validation_failures":
                self.validation_failures,

            "commit_failures":
                self.commit_failures,

            "average_commit_time":
                self.average_commit_time,
        }