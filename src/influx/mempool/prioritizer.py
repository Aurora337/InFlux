from __future__ import annotations

from .queue import PendingTransaction


class TransactionPrioritizer:
    """
    Provides deterministic transaction ordering.

    Transactions with higher fees are placed
    before lower-fee transactions.
    """

    def prioritize(
        self,
        transactions: list[PendingTransaction],
    ) -> list[PendingTransaction]:
        """
        Sort transactions by fee.

        Higher fee transactions appear first.
        """

        return sorted(
            transactions,
            key=lambda tx: (
                tx.fee,
                tx.tx_id,
            ),
            reverse=True,
        )

    def priority_score(
        self,
        transaction: PendingTransaction,
    ) -> int:
        """
        Return transaction priority score.
        """

        return transaction.fee