from __future__ import annotations

from typing import Dict, Optional

from .node import Node


class NodeManager:
    """
    Controls multiple local InFlux nodes.

    Useful for simulations, testing networks,
    and future multi-node orchestration.
    """

    def __init__(self) -> None:

        self.nodes: Dict[
            str,
            Node
        ] = {}


    def add(
        self,
        node: Node,
    ) -> None:
        """
        Register a node.
        """

        self.nodes[
            node.identity.node_id
        ] = node


    def remove(
        self,
        node_id: str,
    ) -> None:
        """
        Remove node.
        """

        self.nodes.pop(
            node_id,
            None,
        )


    def lookup(
        self,
        node_id: str,
    ) -> Optional[Node]:
        """
        Find node.
        """

        return self.nodes.get(
            node_id
        )


    def start_all(self) -> None:
        """
        Start every node.
        """

        for node in self.nodes.values():

            node.start()


    def stop_all(self) -> None:
        """
        Stop every node.
        """

        for node in self.nodes.values():

            node.stop()


    def active_nodes(self) -> list[Node]:
        """
        Return active nodes.
        """

        return [
            node
            for node in self.nodes.values()
            if node.is_healthy()
        ]


    def snapshot(self) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            node_id:
                node.snapshot()

            for node_id, node
            in self.nodes.items()
        }