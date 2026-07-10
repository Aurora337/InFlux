from __future__ import annotations

from enum import Enum


class SyncState(str, Enum):
    """
    Deterministic synchronization lifecycle states.
    """

    INITIALIZING = "initializing"

    IDLE = "idle"

    REQUESTING = "requesting"

    RECEIVING = "receiving"

    VERIFYING = "verifying"

    COMPLETE = "complete"

    FAILED = "failed"

    STOPPED = "stopped"