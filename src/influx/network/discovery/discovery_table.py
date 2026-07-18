from __future__ import annotations

from .discovery_record import DiscoveryRecord


class DiscoveryTable:
    """
    Deterministic discovery record registry.
    """


    def __init__(
        self,
    ) -> None:

        self.records: dict[str, DiscoveryRecord] = {}


    def add(
        self,
        record: DiscoveryRecord,
    ) -> bool:
        """
        Add discovery record.
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
        Remove discovery record.
        """

        if node_id not in self.records:
            return False

        del self.records[
            node_id
        ]

        return True


    def lookup(
        self,
        node_id: str,
    ) -> DiscoveryRecord | None:
        """
        Lookup discovery record.
        """

        return self.records.get(
            node_id
        )


    def contains(
        self,
        node_id: str,
    ) -> bool:
        """
        Check if record exists.
        """

        return node_id in self.records


    def active_peers(
        self,
    ) -> list[DiscoveryRecord]:
        """
        Return active discovery records.
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
        Return number of discovery records.
        """

        return len(self.records)


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic discovery snapshot.
        """

        return {
            node_id: record.snapshot()
            for node_id, record in self.records.items()
        }