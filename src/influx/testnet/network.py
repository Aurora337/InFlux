from __future__ import annotations

from dataclasses import dataclass, field

...

@dataclass(slots=True)
class TestnetNetwork:
    """
    Testnet network representation.
    """

    nodes: dict[str, TestnetNode] = field(default_factory=dict)
    validators: list[str] = field(default_factory=list)

    def add_node(
        self,
        node: TestnetNode,
    ) -> None:
        ...
        """
        Add a node to the network.
        """

        if not node.node_id:
            raise NetworkError(
                "invalid node id"
            )

        self.nodes[node.node_id] = node

    def remove_node(
        self,
        node_id: str,
    ) -> None:
        """
        Remove a node.
        """

        self.nodes.pop(
            node_id,
            None,
        )

    def node_count(
        self,
    ) -> int:
        """
        Return number of nodes.
        """

        return len(self.nodes)

    def online_nodes(
        self,
    ) -> list[TestnetNode]:
        """
        Return active nodes.
        """

        return [
            node
            for node in self.nodes.values()
            if node.online
        ]


TestnetNetwork.__test__ = False