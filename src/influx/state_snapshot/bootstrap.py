from __future__ import annotations

from typing import Any

from .snapshot_store import (
    SnapshotStore,
)


class BootstrapLoader:
    """
    Loads verified state for new nodes.
    """

    def __init__(
        self,
        store: SnapshotStore,
    ) -> None:

        self.store = store

    def load(
        self,
        height: int,
    ) -> dict[str, Any] | None:
        """
        Load state from checkpoint.
        """

        snapshot = (
            self.store.get_snapshot(
                height
            )
        )

        if snapshot is None:
            return None

        if not snapshot.verify():
            return None

        return dict(
            snapshot.state
        )

    def latest(
        self,
    ) -> dict[str, Any] | None:
        """
        Load newest verified state.
        """

        snapshot = (
            self.store.latest()
        )

        if snapshot is None:
            return None

        if not snapshot.verify():
            return None

        return dict(
            snapshot.state
        )