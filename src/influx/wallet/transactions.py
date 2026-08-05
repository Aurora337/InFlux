from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json


@dataclass(slots=True)
class TransactionInput:
    """
    Represents a transaction input.
    """

    source_address: str

    amount: int


@dataclass(slots=True)
class TransactionOutput:
    """
    Represents a transaction output.
    """

    destination_address: str

    amount: int


@dataclass(slots=True)
class WalletTransaction:
    """
    Represents a deterministic wallet transaction.
    """

    sender: str

    inputs: list[TransactionInput]

    outputs: list[TransactionOutput]

    timestamp: int

    signature: str | None = None

    transaction_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Generate deterministic transaction ID.
        """

        self.transaction_id = (
            self.calculate_id()
        )

    def calculate_id(
        self,
    ) -> str:
        """
        Calculate transaction hash.
        """

        payload = {
            "sender": self.sender,
            "inputs": [
                {
                    "source_address": item.source_address,
                    "amount": item.amount,
                }
                for item in self.inputs
            ],
            "outputs": [
                {
                    "destination_address": item.destination_address,
                    "amount": item.amount,
                }
                for item in self.outputs
            ],
            "timestamp": self.timestamp,
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
        )

        return hashlib.sha256(
            serialized.encode()
        ).hexdigest()

    def attach_signature(
        self,
        signature: str,
    ) -> None:
        """
        Attach transaction signature.
        """

        self.signature = signature

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Serialize transaction.
        """

        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "inputs": [
                {
                    "source_address": item.source_address,
                    "amount": item.amount,
                }
                for item in self.inputs
            ],
            "outputs": [
                {
                    "destination_address": item.destination_address,
                    "amount": item.amount,
                }
                for item in self.outputs
            ],
            "timestamp": self.timestamp,
            "signature": self.signature,
        }