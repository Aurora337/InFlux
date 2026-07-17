from __future__ import annotations

from dataclasses import dataclass

from influx.network.peer import Peer
from influx.network.registry import PeerRegistry


@dataclass(slots=True)
class NodeDiscovery:
    """
    Deterministic node discovery service.
    """

    registry: PeerRegistry

    def discover(
        self,
        peer: Peer,
    ) -> None:
        """
        Register a newly discovered peer.
        """

        self.registry.register(peer)

    def forget(
        self,
        peer_id: str,
    ) -> None:
        """
        Remove a peer.
        """

        self.registry.unregister(peer_id)

    def peers(self) -> list[Peer]:
        """
        Return all known peers.
        """

        return self.registry.peers()

    def count(self) -> int:
        """
        Number of discovered peers.
        """

        return self.registry.count()