from __future__ import annotations

from .queue import (
    PendingTransaction,
    TransactionQueue,
)


class TransactionEvictor:
    """
    Handles mempool cleanup policies.
    """

    def evict_lowest_fee(
        self,
        queue: TransactionQueue,
    ) -> PendingTransaction | None:
        """
        Remove and return the lowest-fee
        transaction.
        """

        transactions = (
            queue.list_transactions()
        )

        if not transactions:

            return None

        lowest = min(
            transactions,
            key=lambda tx: (
                tx.fee,
                tx.tx_id,
            ),
        )

        queue.remove(
            lowest.tx_id
        )

        return lowest

    def enforce_capacity(
        self,
        queue: TransactionQueue,
        maximum: int,
    ) -> list[PendingTransaction]:
        """
        Reduce queue size to capacity.

        Returns evicted transactions.
        """

        removed: list[
            PendingTransaction
        ] = []

        while queue.size() > maximum:

            transaction = (
                self.evict_lowest_fee(
                    queue
                )
            )

            if transaction is None:

                break

            removed.append(
                transaction
            )

        return removed