from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class DiscoveryPeer:
    """
    Represents a deterministic network peer.
    """

    peer_id: str

    address: str

    port: int

    active: bool = True

    last_seen: float = field(
        default_factory=time
    )


    def touch(
        self,
    ) -> None:
        """
        Update peer heartbeat timestamp.
        """

        self.last_seen = time()


    def activate(
        self,
    ) -> None:
        """
        Activate peer.
        """

        self.active = True


    def deactivate(
        self,
    ) -> None:
        """
        Deactivate peer.
        """

        self.active = False


    def validate(
        self,
    ) -> None:
        """
        Validate peer properties.
        """

        if not self.peer_id:
            raise ValueError(
                "peer id required"
            )

        if not self.address:
            raise ValueError(
                "peer address required"
            )

        if self.port <= 0:
            raise ValueError(
                "invalid peer port"
            )


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic peer snapshot.
        """

        return {
            "peer_id": self.peer_id,
            "address": self.address,
            "port": self.port,
            "active": self.active,
            "last_seen": self.last_seen,
        }