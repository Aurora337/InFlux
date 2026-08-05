from typing import Any, List


class ReplayEngine:
    """
    Deterministic replay engine.

    Reconstructs system state from event history.
    """

    def __init__(self, state_engine):
        self.state_engine = state_engine

    def replay_events(self, events: List[Any]) -> Any:
        """
        Rebuild system state deterministically from event stream.
        """

        self.state_engine.initialize()

        for event in events:
            self.state_engine.apply(event)

        return self.state_engine.get_state()