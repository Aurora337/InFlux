from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransactionMetrics:
    """
    Tracks deterministic mempool activity.
    """

    transactions_received: int = 0

    transactions_validated: int = 0

    transactions_rejected: int = 0

    transactions_scheduled: int = 0

    transactions_executed: int = 0

    duplicates_detected: int = 0

    average_fee: float = 0.0

    def record_received(self) -> None:
        self.transactions_received += 1

    def record_validated(self) -> None:
        self.transactions_validated += 1

    def record_rejected(self) -> None:
        self.transactions_rejected += 1

    def record_scheduled(self) -> None:
        self.transactions_scheduled += 1

    def record_executed(self) -> None:
        self.transactions_executed += 1

    def record_duplicate(self) -> None:
        self.duplicates_detected += 1

    def update_average_fee(
        self,
        fee: float,
    ) -> None:
        """
        Deterministic rolling average fee.
        """

        if self.average_fee == 0.0:
            self.average_fee = fee
            return

        self.average_fee = (
            self.average_fee + fee
        ) / 2.0

    def snapshot(self) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "transactions_received":
                self.transactions_received,

            "transactions_validated":
                self.transactions_validated,

            "transactions_rejected":
                self.transactions_rejected,

            "transactions_scheduled":
                self.transactions_scheduled,

            "transactions_executed":
                self.transactions_executed,

            "duplicates_detected":
                self.duplicates_detected,

            "average_fee":
                self.average_fee,
        }