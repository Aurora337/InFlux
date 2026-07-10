from __future__ import annotations

from enum import Enum


class NodeState(str, Enum):
    """
    Deterministic lifecycle states for an InFlux node.

    Every node in the network must have one
    well-defined operational state.
    """

    CREATED = "created"

    STARTING = "starting"

    SYNCING = "syncing"

    ACTIVE = "active"

    DEGRADED = "degraded"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"