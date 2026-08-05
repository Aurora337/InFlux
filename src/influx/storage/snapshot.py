import json
import time
from typing import Any, Dict


class SnapshotStore:
    """
    Deterministic snapshot storage layer.

    Stores system state at a point in time for replay and recovery.
    """

    def __init__(self):
        self.snapshots = []

    def create_snapshot(self, state: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        snapshot = {
            "timestamp": time.time(),
            "state": state,
            "metadata": metadata
        }

        self.snapshots.append(snapshot)
        return snapshot

    def get_latest(self) -> Dict[str, Any] | None:
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def export(self) -> str:
        return json.dumps(self.snapshots, indent=2)

    def clear(self) -> None:
        self.snapshots = []