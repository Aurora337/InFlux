from __future__ import annotations

from typing import Dict

from influx.network.peer import Peer


class PeerRegistry:
    """
    Deterministic registry of known network peers.
    """

    def __init__(self) -> None:
        self._peers: Dict[str, Peer] = {}

    def register(self, peer: Peer) -> None:
        """
        Register or update a peer.
        """
        self._peers[peer.node_id] = peer

    def unregister(self, node_id: str) -> None:
        """
        Remove a peer.
        """
        self._peers.pop(node_id, None)

    def get(self, node_id: str) -> Peer | None:
        """
        Lookup a peer.
        """
        return self._peers.get(node_id)

    def peers(self) -> list[Peer]:
        """
        Return peers sorted deterministically.
        """
        return sorted(
            self._peers.values(),
            key=lambda peer: peer.node_id,
        )

    def count(self) -> int:
        return len(self._peers)