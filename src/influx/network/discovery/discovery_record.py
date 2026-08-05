from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass(slots=True)
class DiscoveryRecord:
    """
    Represents a discovered network peer.

    Discovery records are temporary network knowledge.
    They do not replace permanent node identity.
    """

    node_id: str

    address: str

    port: int

    role: str = "validator"

    last_seen: float = field(
        default_factory=time
    )

    trust_score: float = 0.0

    active: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    def update_seen(self) -> None:
        """
        Update peer activity timestamp.
        """

        self.last_seen = time()


    def deactivate(self) -> None:
        """
        Mark peer unavailable.
        """

        self.active = False


    def activate(self) -> None:
        """
        Mark peer available.
        """

        self.active = True

        self.update_seen()


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic peer snapshot.
        """

        return {
            "node_id": self.node_id,

            "address": self.address,

            "port": self.port,

            "role": self.role,

            "last_seen": self.last_seen,

            "trust_score": self.trust_score,

            "active": self.active,

            "metadata": dict(self.metadata),
        }