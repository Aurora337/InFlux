from __future__ import annotations

from dataclasses import dataclass

from .exceptions import (
    DuplicateTransactionError,
    InvalidTransactionError,
    TransactionNotFoundError,
)


@dataclass(frozen=True, slots=True)
class PendingTransaction:
    """
    Represents a transaction waiting
    for consensus processing.
    """

    tx_id: str

    payload: dict[str, object]

    fee: int = 0


class TransactionQueue:
    """
    Deterministic transaction queue.

    Stores pending transactions before
    block inclusion.
    """

    def __init__(self) -> None:

        self._transactions: dict[
            str,
            PendingTransaction,
        ] = {}

    def add(
        self,
        transaction: PendingTransaction,
    ) -> None:
        """
        Add transaction to queue.
        """

        if not transaction.tx_id:

            raise InvalidTransactionError(
                "missing transaction id"
            )

        if transaction.tx_id in self._transactions:

            raise DuplicateTransactionError(
                transaction.tx_id
            )

        self._transactions[
            transaction.tx_id
        ] = transaction

    def get(
        self,
        tx_id: str,
    ) -> PendingTransaction:
        """
        Retrieve transaction.
        """

        if tx_id not in self._transactions:

            raise TransactionNotFoundError(
                tx_id
            )

        return self._transactions[
            tx_id
        ]

    def remove(
        self,
        tx_id: str,
    ) -> bool:
        """
        Remove transaction.
        """

        if tx_id in self._transactions:

            del self._transactions[
                tx_id
            ]

            return True

        return False

    def contains(
        self,
        tx_id: str,
    ) -> bool:
        """
        Check transaction existence.
        """

        return tx_id in self._transactions

    def list_transactions(
        self,
    ) -> list[PendingTransaction]:
        """
        Return queued transactions.
        """

        return list(
            self._transactions.values()
        )

    def size(
        self,
    ) -> int:
        """
        Return queue size.
        """

        return len(
            self._transactions
        )