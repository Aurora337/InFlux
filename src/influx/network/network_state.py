from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NetworkState:
    """
    Deterministic snapshot of network coordination state.

    Tracks active peers, synchronization status,
    replication status, and network progression.
    """

    #
    # Network identity
    #

    network_id: str = "influx-network"

    epoch: int = 0

    #
    # Peer tracking
    #

    peers: set[str] = field(
        default_factory=set
    )

    #
    # Synchronization
    #

    sync_active: bool = False

    sync_round: int = 0

    #
    # Replication
    #

    replication_active: bool = False

    replication_round: int = 0

    #
    # Metadata
    #

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    def add_peer(
        self,
        peer_id: str,
    ) -> None:
        """
        Register a network peer.
        """

        self.peers.add(
            peer_id
        )


    def remove_peer(
        self,
        peer_id: str,
    ) -> None:
        """
        Remove a network peer.
        """

        self.peers.discard(
            peer_id
        )


    def peer_count(
        self,
    ) -> int:
        """
        Return active peer count.
        """

        return len(
            self.peers
        )


    def start_sync(
        self,
    ) -> None:
        """
        Begin synchronization round.
        """

        self.sync_active = True

        self.sync_round += 1


    def complete_sync(
        self,
    ) -> None:
        """
        Complete synchronization.
        """

        self.sync_active = False


    def start_replication(
        self,
    ) -> None:
        """
        Begin replication round.
        """

        self.replication_active = True

        self.replication_round += 1


    def complete_replication(
        self,
    ) -> None:
        """
        Complete replication.
        """

        self.replication_active = False


    def increment_epoch(
        self,
    ) -> None:
        """
        Advance network epoch.
        """

        self.epoch += 1


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic state snapshot.
        """

        return {
            "network_id": self.network_id,
            "epoch": self.epoch,
            "peers": sorted(self.peers),
            "peer_count": self.peer_count(),
            "sync_active": self.sync_active,
            "sync_round": self.sync_round,
            "replication_active": self.replication_active,
            "replication_round": self.replication_round,
            "metadata": dict(self.metadata),
        }