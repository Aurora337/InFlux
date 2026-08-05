from __future__ import annotations

from influx.network.peer import Peer
from influx.network.registry import PeerRegistry


class NetworkManager:
    """
    Coordinates peer management.
    """

    def __init__(self) -> None:
        self.registry = PeerRegistry()

    def add_peer(self, peer: Peer) -> None:
        self.registry.register(peer)

    def remove_peer(self, node_id: str) -> None:
        self.registry.unregister(node_id)

    def peers(self) -> list[Peer]:
        return self.registry.peers()