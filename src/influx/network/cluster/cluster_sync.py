from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterSync:
    """
    Tracks synchronization progress.
    """

    synced_nodes: int = 0

    pending_nodes: int = 0

    def synchronized(
        self,
    ) -> bool:
        """
        True when synchronization is complete.
        """

        return self.pending_nodes == 0

    def snapshot(
        self,
    ) -> dict[str, int | bool]:
        return {
            "synced_nodes": self.synced_nodes,
            "pending_nodes": self.pending_nodes,
            "synchronized": self.synchronized(),
        }