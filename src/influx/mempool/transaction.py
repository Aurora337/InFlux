from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any

from .transaction_state import TransactionState


@dataclass(slots=True)
class Transaction:
    """
    Represents one deterministic InFlux transaction.
    """

    transaction_id: str

    sender: str

    receiver: str

    amount: int

    fee: int

    nonce: int

    payload: dict[str, Any]

    created_at: float = field(
        default_factory=time
    )

    state: TransactionState = (
        TransactionState.CREATED
    )

    def validate(self) -> None:
        """
        Move transaction into validation state.
        """

        self.state = (
            TransactionState.VALIDATING
        )

    def mark_valid(self) -> None:
        """
        Mark transaction as valid.
        """

        self.state = (
            TransactionState.VALID
        )

    def schedule(self) -> None:
        """
        Mark transaction as scheduled.
        """

        self.state = (
            TransactionState.SCHEDULED
        )

    def execute(self) -> None:
        """
        Mark transaction as executed.
        """

        self.state = (
            TransactionState.EXECUTED
        )

    def drop(self) -> None:
        """
        Drop transaction.
        """

        self.state = (
            TransactionState.DROPPED
        )

    def snapshot(self) -> dict:
        """
        Deterministic transaction snapshot.
        """

        return {
            "transaction_id":
                self.transaction_id,

            "sender":
                self.sender,

            "receiver":
                self.receiver,

            "amount":
                self.amount,

            "fee":
                self.fee,

            "nonce":
                self.nonce,

            "payload":
                self.payload,

            "created_at":
                self.created_at,

            "state":
                self.state.value,
        }