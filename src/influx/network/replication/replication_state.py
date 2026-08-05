from __future__ import annotations

from enum import Enum


class ReplicationState(str, Enum):
    """
    Deterministic replication lifecycle.
    """

    INITIALIZING = "initializing"

    QUEUED = "queued"

    REPLICATING = "replicating"

    SYNCHRONIZED = "synchronized"

    FAILED = "failed"

    STOPPED = "stopped"