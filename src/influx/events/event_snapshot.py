"""
Deterministic event state snapshots for the InFlux protocol.

Provides snapshot creation, verification, and restoration
for event-driven state management.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .event import Event


@dataclass(slots=True)
class EventSnapshot:
    """
    Deterministic snapshot of event state at a point in time.
    """

    block_height: int
    timestamp: int = 0

    root_hash: str = ""
    tip_hash: str = ""

    events: list[Event] = field(default_factory=list)

    event_count: int = 0

    block_event_hashes: dict[int, str] = field(
        default_factory=dict
    )

    snapshot_id: str = ""

    _hash: Optional[str] = field(
        default=None,
        repr=False
    )

    def __post_init__(self):
        if self.event_count == 0:
            self.event_count = len(self.events)

    def compute_hash(self) -> str:
        canonical = {
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "root_hash": self.root_hash,
            "tip_hash": self.tip_hash,
            "event_count": self.event_count,
            "events": [
                event.hash for event in self.events
            ],
            "block_event_hashes": {
                str(k): v
                for k, v in sorted(
                    self.block_event_hashes.items()
                )
            },
            "snapshot_id": self.snapshot_id,
        }

        serialized = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    @property
    def hash(self) -> str:
        if self._hash is None:
            self._hash = self.compute_hash()

        return self._hash

    def verify(self) -> bool:
        """
        Verify snapshot integrity.

        Checks:
        - stored hash integrity
        - event count consistency
        - root hash consistency
        - tip hash consistency
        """

        # Event count must match events
        if self.event_count != len(self.events):
            return False

        # Empty snapshot rules
        if not self.events:
            return self.root_hash in ("", None) and self.tip_hash in ("", None)

        event_hashes = [
            event.hash
            for event in self.events
        ]

        # Verify tip hash matches final event
        if self.tip_hash != event_hashes[-1]:
            return False

        # Verify root hash matches first event
        if self.root_hash != event_hashes[0]:
            return False

        # Verify snapshot hash itself
        if self._hash is not None:
            return self._hash == self.compute_hash()

        return True

    def snapshot(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "root_hash": self.root_hash,
            "tip_hash": self.tip_hash,
            "event_count": self.event_count,
            "block_event_hashes": self.block_event_hashes,
            "hash": self.hash,
        }


@dataclass(slots=True)
class EventSnapshotManager:

    _snapshots: dict[str, EventSnapshot] = field(
        default_factory=dict
    )

    _snapshots_by_height: dict[int, str] = field(
        default_factory=dict
    )


    def create_snapshot(
        self,
        events: list[Event],
        block_height: int,
        root_hash: Optional[str] = None,
        tip_hash: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> EventSnapshot:

        if timestamp is None:
            timestamp = int(
                datetime.now(timezone.utc).timestamp()
            )


        event_hashes = [
            event.hash for event in events
        ]


        if root_hash is None:
            root_hash = hashlib.sha256(
                "".join(event_hashes)
                .encode("utf-8")
            ).hexdigest()


        if tip_hash is None:
            tip_hash = (
                event_hashes[-1]
                if event_hashes
                else ""
            )


        block_event_hashes = {
            block_height: root_hash
        }


        snapshot_id = hashlib.sha256(
            json.dumps(
                {
                    "block_height": block_height,
                    "timestamp": timestamp,
                    "root_hash": root_hash,
                    "tip_hash": tip_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:32]


        snapshot = EventSnapshot(
            block_height=block_height,
            timestamp=timestamp,
            root_hash=root_hash,
            tip_hash=tip_hash,
            events=list(events),
            event_count=len(events),
            block_event_hashes=block_event_hashes,
            snapshot_id=snapshot_id,
        )


        self._snapshots[snapshot_id] = snapshot
        self._snapshots_by_height[block_height] = snapshot_id


        return snapshot


    def get_snapshot(
        self,
        snapshot_id: str
    ) -> Optional[EventSnapshot]:
        return self._snapshots.get(snapshot_id)


    def get_all_snapshots(self) -> list[EventSnapshot]:
        return list(self._snapshots.values())


    def get_snapshot_by_height(
        self,
        block_height: int
    ) -> Optional[EventSnapshot]:

        snapshot_id = (
            self._snapshots_by_height.get(
                block_height
            )
        )

        if snapshot_id is None:
            return None

        return self._snapshots.get(snapshot_id)


    # Compatibility API expected by tests

    def get_snapshot_by_block(
        self,
        block_height: int
    ) -> Optional[EventSnapshot]:

        return self.get_snapshot_by_height(
            block_height
        )


    def get_latest_snapshot(
        self
    ) -> Optional[EventSnapshot]:

        if not self._snapshots_by_height:
            return None

        height = max(
            self._snapshots_by_height.keys()
        )

        return self.get_snapshot_by_height(
            height
        )


    def verify_snapshot(
        self,
        snapshot_id: str
    ) -> bool:

        snapshot = self.get_snapshot(
            snapshot_id
        )

        if snapshot is None:
            return False

        return snapshot.verify()


    def verify_all(self) -> bool:
        return all(
            snapshot.verify()
            for snapshot in self._snapshots.values()
        )


    def get_snapshot_count(self) -> int:
        return len(self._snapshots)


    def snapshot_count(self) -> int:
        return self.get_snapshot_count()


    def get_snapshot_heights(self) -> list[int]:
        return sorted(
            self._snapshots_by_height.keys()
        )


    def snapshot(self) -> dict[str, Any]:

        latest = self.get_latest_snapshot()

        return {
            "snapshot_count": self.get_snapshot_count(),
            "snapshot_heights": self.get_snapshot_heights(),
            "latest_block_height":
                latest.block_height
                if latest
                else None,
        "latest_snapshot":
                latest.snapshot()
                if latest
                else None,
        }


    def reset(self) -> None:
        self._snapshots.clear()
        self._snapshots_by_height.clear()