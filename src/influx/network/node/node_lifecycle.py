from __future__ import annotations

from time import time

from .node_state import NodeState


class NodeLifecycle:
    """
    Controls deterministic node startup and shutdown.
    """

    def __init__(self) -> None:

        self.state = NodeState.CREATED

        self.started_at: float | None = None


    def start(self) -> None:
        """
        Start node lifecycle.
        """

        self.state = NodeState.STARTING

        self.started_at = time()


    def begin_sync(self) -> None:
        """
        Move node into synchronization.
        """

        self.state = NodeState.SYNCING


    def activate(self) -> None:
        """
        Mark node operational.
        """

        self.state = NodeState.ACTIVE


    def degrade(self) -> None:
        """
        Mark node degraded.
        """

        self.state = NodeState.DEGRADED


    def stop(self) -> None:
        """
        Shutdown node.
        """

        self.state = NodeState.STOPPED


    def fail(self) -> None:
        """
        Mark node failed.
        """

        self.state = NodeState.FAILED


    def uptime(self) -> float:
        """
        Return lifecycle uptime.
        """

        if self.started_at is None:
            return 0.0

        return time() - self.started_at


    def snapshot(self) -> dict:
        """
        Deterministic lifecycle snapshot.
        """

        return {
            "state": self.state.value,
            "started_at": self.started_at,
            "uptime": self.uptime(),
        }