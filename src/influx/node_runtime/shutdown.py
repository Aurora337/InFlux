from __future__ import annotations

from .lifecycle import NodeLifecycle


class NodeShutdown:
    """
    Handles deterministic node shutdown.
    """

    def __init__(
        self,
        lifecycle: NodeLifecycle,
    ) -> None:
        self.lifecycle = lifecycle
        self.completed = False

    def execute(self) -> None:
        """
        Shutdown node.
        """

        self.lifecycle.stop()
        self.completed = True