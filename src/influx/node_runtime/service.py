from __future__ import annotations

from dataclasses import dataclass

from .node import RuntimeNode


@dataclass(slots=True)
class NodeService:
    """
    Runtime service attached to node.
    """

    name: str
    node: RuntimeNode
    active: bool = False

    def start(self) -> None:
        """
        Start service.
        """

        self.active = True

    def stop(self) -> None:
        """
        Stop service.
        """

        self.active = False