from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4
from typing import Any


@dataclass(slots=True)
class GossipMessage:
    """
    Represents information propagated through
    the InFlux gossip network.

    Messages are intentionally independent from
    transactions and consensus objects.
    """

    origin: str

    payload: dict[str, Any]

    message_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: float = field(
        default_factory=time
    )

    ttl: int = 8

    signature: str = ""

    hops: int = 0


    def decrement_ttl(self) -> bool:
        """
        Reduce remaining propagation distance.

        Returns False when expired.
        """

        if self.ttl <= 0:
            return False

        self.ttl -= 1

        self.hops += 1

        return self.ttl > 0


    def expired(self) -> bool:
        """
        Determine if message can continue.
        """

        return self.ttl <= 0


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic message snapshot.
        """

        return {
            "message_id":
                self.message_id,

            "origin":
                self.origin,

            "payload":
                dict(self.payload),

            "timestamp":
                self.timestamp,

            "ttl":
                self.ttl,

            "signature":
                self.signature,

            "hops":
                self.hops,
        }