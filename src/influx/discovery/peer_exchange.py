from __future__ import annotations

from .registry import (
    PeerRecord,
    PeerRegistry,
)


class PeerExchange:
    """
    Handles peer information exchange.
    """

    def __init__(
        self,
        registry: PeerRegistry,
    ) -> None:

        self._registry = registry

    def announce(
        self,
        peer: PeerRecord,
    ) -> None:
        """
        Announce a peer.
        """

        self._registry.register(
            peer
        )

    def share(
        self,
    ) -> list[PeerRecord]:
        """
        Return peers available for sharing.
        """

        return self._registry.list_peers()

    def merge(
        self,
        peers: list[PeerRecord],
    ) -> None:
        """
        Merge received peers.
        """

        for peer in peers:

            self._registry.register(
                peer
            )