"""state_machine.py

Simple deterministic state machine placeholder for economic transitions.
"""

from enum import Enum, auto


class EconState(Enum):
    IDLE = auto()
    REPRODUCE = auto()
    DECAY = auto()


class EconStateMachine:
    def __init__(self):
        self.state = EconState.IDLE

    def transition(self, event: str) -> EconState:
        if event == "reproduce":
            self.state = EconState.REPRODUCE
        elif event == "decay":
            self.state = EconState.DECAY
        else:
            self.state = EconState.IDLE
        return self.state

__all__ = ["EconState", "EconStateMachine"]
