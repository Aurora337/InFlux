from __future__ import annotations

from typing import Dict

from .transaction import Transaction


class TransactionPool:
    """
    Deterministic transaction mempool.
    """

    def __init__(self) -> None:

        self._transactions: Dict[
            str,
            Transaction,
        ] = {}

    def add(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Add transaction if unique.
        """

        if (
            transaction.transaction_id
            in self._transactions
        ):
            return False

        self._transactions[
            transaction.transaction_id
        ] = transaction

        return True

    def remove(
        self,
        transaction_id: str,
    ) -> bool:
        """
        Remove transaction.
        """

        if (
            transaction_id
            not in self._transactions
        ):
            return False

        del self._transactions[
            transaction_id
        ]

        return True

    def lookup(
        self,
        transaction_id: str,
    ) -> Transaction | None:
        """
        Find transaction.
        """

        return self._transactions.get(
            transaction_id
        )

    def pending(
        self,
    ) -> list[Transaction]:
        """
        Return transactions.

        Deterministic ordering handled
        by scheduler.
        """

        return list(
            self._transactions.values()
        )

    def size(
        self,
    ) -> int:
        """
        Return pool size.
        """

        return len(
            self._transactions
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic pool snapshot.
        """

        return {
            transaction_id:
                self._transactions[
                    transaction_id
                ].snapshot()
            for transaction_id
            in sorted(
                self._transactions
            )
        }