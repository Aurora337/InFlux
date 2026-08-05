from __future__ import annotations

from enum import Enum


class NodeState(str, Enum):
    """
    Deterministic lifecycle states for a network node.
    """

    CREATED = "created"
    STARTING = "starting"
    SYNCING = "syncing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAILED = "failed"