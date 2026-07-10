from __future__ import annotations

from enum import Enum


class DiscoveryState(str, Enum):
    """
    Deterministic states for peer discovery.

    Discovery state is independent from node state.
    A node may be active while discovery is refreshing.
    """

    INITIALIZING = "initializing"

    DISCOVERING = "discovering"

    ACTIVE = "active"

    DEGRADED = "degraded"

    STOPPED = "stopped"

    FAILED = "failed"