from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TransactionRequest:
    """
    SDK transaction request.
    """

    sender: str

    recipient: str

    amount: int

    fee: int = 0

    metadata: dict[str, object] = field(
        default_factory=dict,
    )


@dataclass(frozen=True, slots=True)
class SignedTransaction:
    """
    Signed transaction container.
    """

    tx_id: str

    request: TransactionRequest

    signature: str