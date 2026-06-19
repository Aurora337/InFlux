"""Store and retrieve recorded state snapshots with their deterministic hashes."""

from dataclasses import dataclass, asdict
import json
from typing import Optional


@dataclass(frozen=True)
class StateSnapshot:
    epoch: int
    state_hash: str
    state_dict: dict


class ReplayStore:
    def __init__(self):
        self.snapshots: list[StateSnapshot] = []

    def record(self, epoch: int, state_hash: str, state_dict: dict) -> None:
        snapshot = StateSnapshot(
            epoch=epoch,
            state_hash=state_hash,
            state_dict=state_dict,
        )
        self.snapshots.append(snapshot)

    def load_by_epoch(self, epoch: int) -> Optional[StateSnapshot]:
        for snapshot in self.snapshots:
            if snapshot.epoch == epoch:
                return snapshot
        return None

    def export_json(self) -> str:
        data = [asdict(s) for s in self.snapshots]
        return json.dumps(data, indent=2)

    def import_json(self, json_str: str) -> None:
        data = json.loads(json_str)
        self.snapshots = [
            StateSnapshot(
                epoch=item["epoch"],
                state_hash=item["state_hash"],
                state_dict=item["state_dict"],
            )
            for item in data
        ]

    def all_snapshots(self) -> list[StateSnapshot]:
        return self.snapshots


__all__ = ["ReplayStore", "StateSnapshot"]
