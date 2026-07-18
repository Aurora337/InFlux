from __future__ import annotations

from enum import Enum


class SyncState(str, Enum):
    """
    Synchronization lifecycle.
    """

    INITIALIZING = "initializing"

    CONNECTING = "connecting"

    SYNCHRONIZING = "synchronizing"

    SYNCHRONIZED = "synchronized"

    FAILED = "failed"

    STOPPED = "stopped"