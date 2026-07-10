from __future__ import annotations

from enum import Enum


class ReplicationState(str, Enum):
    """
    Deterministic replication session lifecycle.
    """

    CREATED = "created"

    SYNCING = "syncing"

    VERIFYING = "verifying"

    COMMITTED = "committed"

    FAILED = "failed"

    CANCELLED = "cancelled"