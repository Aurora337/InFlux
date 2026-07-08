from typing import Any, Dict

from influx.crypto.hash import DeterministicHasher


class StateEngine:
    """
    Deterministic State Engine (Execution Grade)

    This is now a real state transition system, not a stub.
    """

    def __init__(self, config: dict):
        self.config = config
        self.state: Dict[str, Any] = {}
        self.state_hash: str | None = None
        self.version_cursor: int = 0

    def initialize(self) -> None:
        self.state = {}
        self.version_cursor = 0
        self.state_hash = self._compute_hash()

    # -----------------------------
    # CORE STATE TRANSITION LOGIC
    # -----------------------------

    def apply(self, event: Any) -> Dict[str, Any]:
        """
        Deterministic state transition function.
        """

        event_type = event.get("type", "UNKNOWN")
        payload = event.get("payload", {})

        # Deterministic key derivation
        key = DeterministicHasher.hash(event_type)

        # Deterministic merge rule
        if key not in self.state:
            self.state[key] = []

        self.state[key].append({
            "payload": payload,
            "version": self.version_cursor
        })

        self.version_cursor += 1

        # Recompute state hash after every transition
        self.state_hash = self._compute_hash()

        return self.state

    # -----------------------------
    # STATE ACCESS
    # -----------------------------

    def get_state(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "state_hash": self.state_hash,
            "version": self.version_cursor
        }

    # -----------------------------
    # REPLAY ENGINE (CORE FEATURE)
    # -----------------------------

    def replay(self, events: Any) -> Dict[str, Any]:
        """
        Fully deterministic replay of event history.
        """

        self.initialize()

        for event in events:
            self.apply(event)

        return self.get_state()

    # -----------------------------
    # INTERNAL HASHING
    # -----------------------------

    def _compute_hash(self) -> str:
        """
        Deterministic fingerprint of entire state.
        """
        return DeterministicHasher.hash({
            "state": self.state,
            "version": self.version_cursor
        })