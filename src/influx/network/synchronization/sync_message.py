from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4
from typing import Any


@dataclass(slots=True)
class SyncMessage:
    """
    Base synchronization message.

    Represents communication between nodes
    during state synchronization.
    """

    source_node: str

    target_node: str

    payload: dict[str, Any]

    message_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: float = field(
        default_factory=time
    )

    state_hash: str = ""

    signature: str = ""


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic message snapshot.
        """

        return {
            "message_id":
                self.message_id,

            "source_node":
                self.source_node,

            "target_node":
                self.target_node,

            "payload":
                dict(self.payload),

            "timestamp":
                self.timestamp,

            "state_hash":
                self.state_hash,

            "signature":
                self.signature,
        }