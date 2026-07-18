from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4


@dataclass(slots=True)
class GossipMessage:
    """
    Deterministic gossip propagation message.
    """

    origin: str

    payload: dict[str, object]

    message_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    signature: str = ""

    ttl: int = 8

    hops: int = 0

    created_at: float = field(
        default_factory=time
    )


    def decrement_ttl(
        self,
    ) -> bool:
        """
        Reduce message lifetime and record propagation hop.
        """

        if self.ttl > 0:
            self.ttl -= 1

        self.hops += 1

        return True


    def increment_hop(
        self,
    ) -> None:
        """
        Increment propagation hops.
        """

        self.hops += 1


    def expired(
        self,
    ) -> bool:
        """
        Determine whether message expired.
        """

        return self.ttl <= 0


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic message snapshot.
        """

        return {
            "message_id": self.message_id,
            "origin": self.origin,
            "payload": self.payload,
            "signature": self.signature,
            "ttl": self.ttl,
            "hops": self.hops,
            "created_at": self.created_at,
        }