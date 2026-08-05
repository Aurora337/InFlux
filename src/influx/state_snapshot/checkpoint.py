from __future__ import annotations

from dataclasses import dataclass

from .snapshot import (
    StateSnapshot,
)


@dataclass(slots=True)
class Checkpoint:
    """
    Represents a verified network checkpoint.
    """

    height: int

    root_hash: str

    snapshot_hash: str

    @classmethod
    def from_snapshot(
        cls,
        snapshot: StateSnapshot,
    ) -> "Checkpoint":
        """
        Create checkpoint from snapshot.
        """

        data = (
            f"{snapshot.height}:"
            f"{snapshot.root_hash}"
        )

        import hashlib

        snapshot_hash = hashlib.sha256(
            data.encode()
        ).hexdigest()

        return cls(
            height=snapshot.height,
            root_hash=snapshot.root_hash,
            snapshot_hash=snapshot_hash,
        )

    def verify(
        self,
        snapshot: StateSnapshot,
    ) -> bool:
        """
        Verify checkpoint matches snapshot.
        """

        checkpoint = (
            Checkpoint.from_snapshot(
                snapshot
            )
        )

        return (
            checkpoint.snapshot_hash
            ==
            self.snapshot_hash
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic checkpoint output.
        """

        return {
            "height":
                self.height,

            "root_hash":
                self.root_hash,

            "snapshot_hash":
                self.snapshot_hash,
        }