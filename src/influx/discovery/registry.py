from __future__ import annotations

from dataclasses import dataclass

from .exceptions import (
    InvalidPeerError,
    PeerNotFoundError,
)


@dataclass(frozen=True, slots=True)
class PeerRecord:
    """
    Represents a discovered network peer.
    """

    node_id: str

    address: str

    port: int

    active: bool = True


class PeerRegistry:
    """
    Deterministic peer registry.

    Maintains known network peers.
    """

    def __init__(
        self,
    ) -> None:

        self._peers: dict[
            str,
            PeerRecord,
        ] = {}

    def register(
        self,
        peer: PeerRecord,
    ) -> None:
        """
        Register a peer.
        """

        if not peer.node_id:

            raise InvalidPeerError(
                "missing node id"
            )

        if not peer.address:

            raise InvalidPeerError(
                "missing address"
            )

        self._peers[
            peer.node_id
        ] = peer

    def get(
        self,
        node_id: str,
    ) -> PeerRecord:
        """
        Retrieve peer.
        """

        if node_id not in self._peers:

            raise PeerNotFoundError(
                node_id
            )

        return self._peers[
            node_id
        ]

    def remove(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove peer.
        """

        if node_id in self._peers:

            del self._peers[
                node_id
            ]

            return True

        return False

    def exists(
        self,
        node_id: str,
    ) -> bool:
        """
        Check peer existence.
        """

        return node_id in self._peers

    def list_peers(
        self,
    ) -> list[PeerRecord]:
        """
        Return deterministic peer list.
        """

        return list(
            self._peers.values()
        )

    def count(
        self,
    ) -> int:
        """
        Return peer count.
        """

        return len(
            self._peers
        )