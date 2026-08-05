from __future__ import annotations

from influx.network.peer import Peer


class NetworkTopology:
    """
    Deterministic peer topology.
    """

    def __init__(self) -> None:
        self._peers: dict[str, Peer] = {}

    def add(self, peer: Peer) -> None:
        self._peers[peer.node_id] = peer

    def remove(self, node_id: str) -> None:
        self._peers.pop(node_id, None)

    def peers(self) -> list[Peer]:
        return sorted(
            self._peers.values(),
            key=lambda p: p.node_id,
        )