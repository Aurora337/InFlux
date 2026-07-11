from __future__ import annotations

from dataclasses import dataclass

from .node import TestnetNode

from .exceptions import NodeError


@dataclass(slots=True)
class FaultInjector:
    """
    Deterministic testnet fault controller.
    """

    def disconnect(
        self,
        node: TestnetNode,
    ) -> None:
        """
        Simulate node failure.
        """

        if not node.node_id:
            raise NodeError(
                "invalid node"
            )

        node.online = False

    def reconnect(
        self,
        node: TestnetNode,
    ) -> None:
        """
        Restore node operation.
        """

        node.online = True