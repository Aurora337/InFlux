from __future__ import annotations

from .node import RuntimeNode


class NodeManager:
    """
    Manages runtime nodes.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, RuntimeNode] = {}

    def register(
        self,
        node: RuntimeNode,
    ) -> None:
        """
        Register runtime node.
        """

        self.nodes[node.configuration.node_id] = node

    def remove(
        self,
        node_id: str,
    ) -> None:
        """
        Remove runtime node.
        """

        self.nodes.pop(
            node_id,
            None,
        )

    def get(
        self,
        node_id: str,
    ) -> RuntimeNode | None:
        """
        Retrieve node.
        """

        return self.nodes.get(node_id)

    def count(self) -> int:
        """
        Return node count.
        """

        return len(self.nodes)