from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TransactionRecord:
    """
    Explorer transaction representation.
    """

    tx_id: str

    sender: str

    recipient: str

    amount: int

    block_height: int | None = None

    confirmed: bool = False