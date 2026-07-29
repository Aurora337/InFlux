"""
Deterministic economic state snapshots for the InFlux protocol.

Provides snapshot creation, verification, and restoration
for the EconomicState at block boundaries.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .economic_state import EconomicState


@dataclass(slots=True)
class EconomicSnapshot:
    """
    Deterministic snapshot of the EconomicState at a point in time.

    Captures the full state for audit, replay, and consensus verification.
    """

    block_height: int
    timestamp: int
    state_root: str
    state_hash: str
    account_count: int
    total_supply: float
    circulating_supply: float
    reserve_size: float
    reserve_ratio: float
    current_epoch: int
    snapshot_id: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute the deterministic hash of this snapshot."""
        canonical = {
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "state_root": self.state_root,
            "state_hash": self.state_hash,
            "account_count": self.account_count,
            "total_supply": str(self.total_supply),
            "circulating_supply": str(self.circulating_supply),
            "reserve_size": str(self.reserve_size),
            "reserve_ratio": str(self.reserve_ratio),
            "current_epoch": self.current_epoch,
            "snapshot_id": self.snapshot_id,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def verify(self) -> bool:
        """Verify the snapshot's hash integrity."""
        return self.hash == self.compute_hash()

    def snapshot(self) -> dict[str, Any]:
        """Deterministic snapshot metadata."""
        return {
            "snapshot_id": self.snapshot_id,
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "state_root": self.state_root,
            "state_hash": self.state_hash,
            "account_count": self.account_count,
            "total_supply": str(self.total_supply),
            "circulating_supply": str(self.circulating_supply),
            "reserve_size": str(self.reserve_size),
            "reserve_ratio": str(self.reserve_ratio),
            "current_epoch": self.current_epoch,
            "hash": self.hash,
        }


@dataclass(slots=True)
class EconomicSnapshotManager:
    """
    Manages economic state snapshots.

    Provides:
    - Snapshot creation at block boundaries
    - Snapshot verification against current state
    - Snapshot history tracking
    - State restoration from snapshots
    """

    _snapshots: dict[str, EconomicSnapshot] = field(default_factory=dict)
    _snapshots_by_height: dict[int, str] = field(default_factory=dict)

    def create_snapshot(
        self,
        state: EconomicState,
        block_height: int,
        timestamp: Optional[int] = None,
    ) -> EconomicSnapshot:
        """
        Create a snapshot of the current economic state.

        Args:
            state: The economic state to snapshot
            block_height: The current block height
            timestamp: Unix timestamp (defaults to current time)

        Returns:
            An EconomicSnapshot capturing the state
        """
        if timestamp is None:
            timestamp = int(datetime.now(timezone.utc).timestamp())

        snapshot_id = hashlib.sha256(
            json.dumps(
                {
                    "block_height": block_height,
                    "timestamp": timestamp,
                    "state_root": state.state_root,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()[:32]

        snapshot = EconomicSnapshot(
            block_height=block_height,
            timestamp=timestamp,
            state_root=state.state_root,
            state_hash=state.hash,
            account_count=len(state.accounts),
            total_supply=state.supply.total_supply,
            circulating_supply=state.supply.circulating_supply,
            reserve_size=state.reserve.reserve_size,
            reserve_ratio=state.reserve.current_ratio,
            current_epoch=state.current_epoch,
            snapshot_id=snapshot_id,
        )

        self._snapshots[snapshot_id] = snapshot
        self._snapshots_by_height[block_height] = snapshot_id

        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[EconomicSnapshot]:
        """Get a snapshot by its ID."""
        return self._snapshots.get(snapshot_id)

    def get_snapshot_by_height(self, block_height: int) -> Optional[EconomicSnapshot]:
        """Get the snapshot at a specific block height."""
        snapshot_id = self._snapshots_by_height.get(block_height)
        if snapshot_id is None:
            return None
        return self._snapshots.get(snapshot_id)

    def verify_snapshot(self, snapshot_id: str) -> bool:
        """
        Verify a snapshot's integrity.

        Args:
            snapshot_id: The snapshot to verify

        Returns:
            True if the snapshot is valid
        """
        snapshot = self.get_snapshot(snapshot_id)
        if snapshot is None:
            return False
        return snapshot.verify()

    def verify_snapshot_against_state(
        self, snapshot_id: str, state: EconomicState
    ) -> bool:
        """
        Verify a snapshot against the current state.

        Args:
            snapshot_id: The snapshot to verify
            state: The current economic state

        Returns:
            True if the snapshot matches the state
        """
        snapshot = self.get_snapshot(snapshot_id)
        if snapshot is None:
            return False
        if not snapshot.verify():
            return False
        if snapshot.state_root != state.state_root:
            return False
        if snapshot.state_hash != state.hash:
            return False
        return True

    def get_snapshot_count(self) -> int:
        """Get the number of stored snapshots."""
        return len(self._snapshots)

    def get_snapshot_heights(self) -> list[int]:
        """Get all block heights with snapshots."""
        return sorted(self._snapshots_by_height.keys())

    def snapshot(self) -> dict[str, Any]:
        """Deterministic snapshot manager state."""
        return {
            "snapshot_count": self.get_snapshot_count(),
            "snapshot_heights": self.get_snapshot_heights(),
            "latest_snapshot": self._snapshots[
                self._snapshots_by_height[max(self._snapshots_by_height.keys())]
            ].snapshot() if self._snapshots_by_height else None,
        }

    def reset(self) -> None:
        """Reset the snapshot manager."""
        self._snapshots.clear()
        self._snapshots_by_height.clear()
