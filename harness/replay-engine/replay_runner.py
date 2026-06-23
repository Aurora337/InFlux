"""Execute replay cycles and recompute state hashes for verification."""

import sys
sys.path.insert(0, "src")

from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from replay_store import StateSnapshot


class ReplayRunner:
    def __init__(self):
        self.replay_results = []

    def replay_single(self, snapshot: StateSnapshot) -> dict:
        """
        Reload a recorded state snapshot and recompute its hash.
        """
        recorded_hash = snapshot.state_hash
        
        # Reconstruct state from dict
        state = State(
            epoch=snapshot.state_dict["epoch"],
            supply=snapshot.state_dict["supply"],
            participants=snapshot.state_dict["participants"],
        )
        
        # Recompute hash
        serialized = serialize_state(state)
        recomputed_hash = compute_root_hash(serialized)
        
        # Compare
        match = recorded_hash == recomputed_hash
        
        result = {
            "epoch": snapshot.epoch,
            "recorded_hash": recorded_hash,
            "recomputed_hash": recomputed_hash,
            "match": match,
            "state": state,
        }
        
        self.replay_results.append(result)
        return result

    def replay_all(self, snapshots: list[StateSnapshot]) -> list[dict]:
        """Replay all snapshots in sequence."""
        results = []
        for snapshot in snapshots:
            result = self.replay_single(snapshot)
            results.append(result)
        return results

    def all_match(self) -> bool:
        """Check if all replayed hashes matched their recorded counterparts."""
        return all(result["match"] for result in self.replay_results)


__all__ = ["ReplayRunner"]
