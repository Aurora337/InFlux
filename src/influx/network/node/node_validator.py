from __future__ import annotations

from dataclasses import dataclass

from .network_node import NetworkNode
from .node_state import NodeState


@dataclass(slots=True)
class NodeValidator:
    """
    Deterministic validator for network nodes.
    """

    def validate(
        self,
        node: NetworkNode,
    ) -> bool:
        """
        Validate whether a node is correctly configured.
        """

        if not node.node_id:
            return False

        try:
            node.config.validate()
        except ValueError:
            return False

        return True

    def ready(
        self,
        node: NetworkNode,
    ) -> bool:
        """
        Determine whether a node is ready to
        participate in the network.
        """

        return (
            self.validate(node)
            and node.state == NodeState.ACTIVE
        )