from __future__ import annotations

from dataclasses import dataclass

from .node import RuntimeNode


@dataclass(slots=True)
class NodeLifecycle:
    """
    Controls runtime node lifecycle.
    """

    node: RuntimeNode
    running: bool = False

    def start(self) -> None:
        """
        Start node lifecycle.
        """

        self.node.start()
        self.running = True

    def stop(self) -> None:
        """
        Stop node lifecycle.
        """

        self.node.stop()
        self.running = False

    def is_running(self) -> bool:
        """
        Return lifecycle status.
        """

        return self.running