from __future__ import annotations

from dataclasses import dataclass

from .sync_snapshot import SyncSnapshot


@dataclass(slots=True)
class SyncValidator:
    """
    Validates synchronization snapshots.
    """

    def validate(
        self,
        snapshot: SyncSnapshot,
    ) -> bool:
        """
        Validate a snapshot.
        """

        if snapshot.height < 0:
            return False

        if not snapshot.snapshot_id:
            return False

        if not snapshot.state_hash:
            return False

        return True