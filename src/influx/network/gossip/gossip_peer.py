from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class GossipPeer:
    """
    Represents a gossip network peer.
    """

    node_id: str

    address: str

    port: int

    active: bool = True

    last_seen: float = field(
        default_factory=time
    )


    def mark_seen(
        self,
    ) -> None:
        """
        Update peer activity timestamp.
        """

        self.last_seen = time()


    def deactivate(
        self,
    ) -> None:
        """
        Disable peer.
        """

        self.active = False


    def activate(
        self,
    ) -> None:
        """
        Enable peer.
        """

        self.active = True


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic peer snapshot.
        """

        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "active": self.active,
            "last_seen": self.last_seen,
        }