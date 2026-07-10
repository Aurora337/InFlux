from __future__ import annotations

from enum import Enum


class GossipState(str, Enum):
    """
    Deterministic states for gossip operation.
    """

    INITIALIZING = "initializing"

    ACTIVE = "active"

    PROPAGATING = "propagating"

    DEGRADED = "degraded"

    STOPPED = "stopped"

    FAILED = "failed"