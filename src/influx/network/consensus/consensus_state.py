from __future__ import annotations

from enum import Enum


class ConsensusState(str, Enum):
    """
    Deterministic consensus lifecycle.
    """

    IDLE = "idle"

    PROPOSING = "proposing"

    VOTING = "voting"

    COMMITTED = "committed"

    FAILED = "failed"