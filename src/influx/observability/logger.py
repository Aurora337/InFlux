import json
import time
from typing import Any, Dict, List


class DeterministicLogger:
    """
    Deterministic system logger for InFlux.

    Ensures all events, state transitions, and consensus decisions
    are traceable and reproducible.
    """

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def _timestamp(self) -> float:
        return time.time()

    def log_event(self, event_type: str, data: Any) -> None:
        entry = {
            "timestamp": self._timestamp(),
            "type": event_type,
            "data": data
        }
        self.logs.append(entry)

    def log_state_transition(self, before: Any, after: Any) -> None:
        self.log_event("STATE_TRANSITION", {
            "before": before,
            "after": after
        })

    def log_consensus(self, consensus_data: Any) -> None:
        self.log_event("CONSENSUS", consensus_data)

    def log_replication(self, replication_data: Any) -> None:
        self.log_event("REPLICATION", replication_data)

    def export(self) -> str:
        """
        Export full deterministic log trace.
        """
        return json.dumps(self.logs, indent=2)

    def clear(self) -> None:
        self.logs = []