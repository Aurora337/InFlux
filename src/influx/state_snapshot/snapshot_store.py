from __future__ import annotations

from .snapshot import (
    StateSnapshot,
)

from .checkpoint import (
    Checkpoint,
)


class SnapshotStore:
    """
    Stores deterministic state snapshots.
    """

    def __init__(
        self,
    ) -> None:

        self._snapshots: dict[
            int,
            StateSnapshot,
        ] = {}

        self._checkpoints: dict[
            int,
            Checkpoint,
        ] = {}

    def save(
        self,
        snapshot: StateSnapshot,
    ) -> Checkpoint:
        """
        Save snapshot and create checkpoint.
        """

        checkpoint = (
            Checkpoint.from_snapshot(
                snapshot
            )
        )

        self._snapshots[
            snapshot.height
        ] = snapshot

        self._checkpoints[
            snapshot.height
        ] = checkpoint

        return checkpoint

    def get_snapshot(
        self,
        height: int,
    ) -> StateSnapshot | None:
        """
        Retrieve snapshot by height.
        """

        return self._snapshots.get(
            height
        )

    def get_checkpoint(
        self,
        height: int,
    ) -> Checkpoint | None:
        """
        Retrieve checkpoint by height.
        """

        return self._checkpoints.get(
            height
        )

    def latest(
        self,
    ) -> StateSnapshot | None:
        """
        Return latest stored snapshot.
        """

        if not self._snapshots:
            return None

        height = max(
            self._snapshots.keys()
        )

        return self._snapshots[
            height
        ]