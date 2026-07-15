from __future__ import annotations

from dataclasses import dataclass

from .node import TestnetNode
from .network import TestnetNetwork


@dataclass(slots=True)
class TestnetDeployment:
    """
    Testnet deployment coordinator.
    """

    __test__ = False
    network: TestnetNetwork

    def deploy_node(
        self,
        node_id: str,
        validator: bool = False,
    ) -> TestnetNode:
        """
        Create and deploy a node.
        """

        node = TestnetNode(
            node_id=node_id,
            validator=validator,
        )

        node.start()

        self.network.add_node(
            node,
        )

        return node

    def shutdown(
        self,
    ) -> None:
        """
        Stop all deployed nodes.
        """

        for node in self.network.nodes.values():
            node.stop()