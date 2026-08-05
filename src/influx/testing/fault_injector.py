import random
from typing import Any, Dict


class FaultInjector:
    """
    Deterministic fault injection system.

    Used to simulate adversarial or degraded network conditions.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    # -----------------------------
    # NODE FAILURE SIMULATION
    # -----------------------------

    def maybe_crash_node(self, node: Any, crash_probability: float = 0.0) -> bool:
        """
        Simulates node failure.
        """
        if random.random() < crash_probability:
            node.stop()
            return True
        return False

    # -----------------------------
    # EVENT CORRUPTION
    # -----------------------------

    def corrupt_event(self, event: Dict[str, Any], corruption_rate: float = 0.0) -> Dict[str, Any]:
        """
        Deterministically corrupts event payload.
        """

        if random.random() < corruption_rate:
            event = event.copy()
            event["corrupted"] = True
            event["payload"] = {"tampered": True}

        return event

    # -----------------------------
    # NETWORK DELAY SIMULATION
    # -----------------------------

    def maybe_delay(self, delay_probability: float = 0.0) -> float:
        """
        Returns artificial delay in seconds.
        """

        if random.random() < delay_probability:
            return random.uniform(0.1, 0.5)

        return 0.0

    # -----------------------------
    # MESSAGE DROPPING
    # -----------------------------

    def should_drop_message(self, drop_rate: float = 0.0) -> bool:
        return random.random() < drop_rate

    # -----------------------------
    # BATCH FAULT APPLICATION
    # -----------------------------

    def apply_faults(
        self,
        event: Dict[str, Any],
        corruption_rate: float = 0.0,
        drop_rate: float = 0.0
    ) -> Dict[str, Any] | None:

        if self.should_drop_message(drop_rate):
            return None

        return self.corrupt_event(event, corruption_rate)