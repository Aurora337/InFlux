from __future__ import annotations

from enum import Enum


class ClusterState(str, Enum):
    """
    Deterministic cluster lifecycle states.
    """

    INITIALIZING = "initializing"

    FORMING = "forming"

    ACTIVE = "active"

    DEGRADED = "degraded"

    RECOVERING = "recovering"

    STOPPED = "stopped"

    FAILED = "failed"