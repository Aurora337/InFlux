from __future__ import annotations

from influx.mempool.transaction import Transaction


class BlockScheduler:
    """
    Creates deterministic transaction sets
    for block assembly.
    """

    @staticmethod
    def order(
        transactions: list[Transaction],
    ) -> list[Transaction]:
        """
        Deterministic transaction ordering.

        Priority:
        1. Higher fee
        2. Lower nonce
        3. Transaction ID
        """

        return sorted(
            transactions,
            key=lambda tx: (
                -tx.fee,
                tx.nonce,
                tx.transaction_id,
            ),
        )

    @classmethod
    def select(
        cls,
        transactions: list[Transaction],
        limit: int,
    ) -> list[Transaction]:
        """
        Select transactions for block.
        """

        return cls.order(
            transactions
        )[:limit]