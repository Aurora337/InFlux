from __future__ import annotations

from .transaction import Transaction


class TransactionScheduler:
    """
    Creates deterministic transaction ordering.
    """

    @staticmethod
    def sort(
        transactions: list[Transaction],
    ) -> list[Transaction]:
        """
        Sort transactions deterministically.

        Priority:
        1. Higher fee
        2. Lower nonce
        3. Transaction ID
        """

        return sorted(
            transactions,
            key=lambda transaction: (
                -transaction.fee,
                transaction.nonce,
                transaction.transaction_id,
            ),
        )

    @classmethod
    def select(
        cls,
        transactions: list[Transaction],
        limit: int,
    ) -> list[Transaction]:
        """
        Select deterministic transaction subset.
        """

        return cls.sort(
            transactions
        )[:limit]

    @classmethod
    def schedule(
        cls,
        transactions: list[Transaction],
    ) -> list[Transaction]:
        """
        Mark transactions scheduled.
        """

        ordered = cls.sort(
            transactions
        )

        for transaction in ordered:
            transaction.schedule()

        return ordered