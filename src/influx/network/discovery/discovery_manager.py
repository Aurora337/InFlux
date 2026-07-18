from __future__ import annotations

from time import time

from .discovery import Discovery
from .discovery_record import DiscoveryRecord


class DiscoveryManager:
    """
    Coordinates discovery operations.
    """


    def __init__(
        self,
        discovery: Discovery | None = None,
    ) -> None:

        self.discovery = (
            discovery
            if discovery is not None
            else Discovery()
        )


    def register_peer(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        """
        Register a discovered peer.
        """

        return self.discovery.discover(
            record
        )


    def remove_peer(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove discovered peer.
        """

        return self.discovery.remove(
            node_id
        )


    def lookup(
        self,
        node_id: str,
    ) -> DiscoveryRecord | None:
        """
        Lookup peer.
        """

        return self.discovery.lookup(
            node_id
        )


    def refresh_peer(
        self,
        node_id: str,
    ) -> bool:
        """
        Refresh peer heartbeat.
        """

        record = self.lookup(
            node_id
        )

        if record is None:
            return False

        record.last_seen = time()

        return True


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Return discovery state snapshot.
        """

        snapshot = self.discovery.snapshot()

        table = snapshot.get(
            "table",
            {},
        )

        if isinstance(table, dict):
            snapshot.update(
                table
            )

        return snapshot