from __future__ import annotations

from typing import Dict, Optional

from .discovery_record import DiscoveryRecord


class DiscoveryTable:
    """
    Stores known peer discovery records.

    The table provides deterministic lookup and
    peer lifecycle management.
    """

    def __init__(self) -> None:

        self.records: Dict[
            str,
            DiscoveryRecord
        ] = {}


    def add(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        """
        Add a peer record.

        Returns False if duplicate.
        """

        if record.node_id in self.records:
            return False

        self.records[
            record.node_id
        ] = record

        return True


    def remove(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove peer record.
        """

        if node_id not in self.records:
            return False

        del self.records[node_id]

        return True


    def lookup(
        self,
        node_id: str,
    ) -> Optional[DiscoveryRecord]:
        """
        Find peer record.
        """

        return self.records.get(
            node_id
        )


    def active_peers(
        self,
    ) -> list[DiscoveryRecord]:
        """
        Return active peers.
        """

        return [
            record
            for record in self.records.values()
            if record.active
        ]


    def count(
        self,
    ) -> int:
        """
        Return peer count.
        """

        return len(
            self.records
        )


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic table snapshot.
        """

        return {
            node_id:
                record.snapshot()

            for node_id, record
            in self.records.items()
        }