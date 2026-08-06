from __future__ import annotations

from dataclasses import dataclass, field

from .network_node import NetworkNode
from .node_state import NodeState


@dataclass(slots=True)
class NodeManager:
    """
    Deterministic manager for network nodes.
    """

    _nodes: dict[str, NetworkNode] = field(
        default_factory=dict
    )

    @staticmethod
    def _node_id(node: object) -> str:
        """Return the identifier used by either supported node representation."""

        node_id = getattr(node, "node_id", None)
        if node_id:
            return node_id

        identity = getattr(node, "identity", None)
        identity_node_id = getattr(identity, "node_id", None)
        if identity_node_id:
            return identity_node_id

        raise ValueError("node must provide a node_id or identity.node_id")

    def register(
        self,
        node: NetworkNode,
    ) -> None:
        self._nodes[self._node_id(node)] = node

    def unregister(
        self,
        node_id: str,
    ) -> None:
        self._nodes.pop(node_id, None)

    def get(
        self,
        node_id: str,
    ) -> NetworkNode | None:
        return self._nodes.get(node_id)

    def nodes(self) -> list[NetworkNode]:
        return sorted(
            self._nodes.values(),
            key=lambda node: node.node_id,
        )

    def count(self) -> int:
        return len(self._nodes)

    # Compatibility API for the higher-level Node implementation.
    def add(self, node: NetworkNode) -> None:
        self.register(node)

    def remove(self, node_id: str) -> None:
        self.unregister(node_id)

    def lookup(self, node_id: str) -> NetworkNode | None:
        return self.get(node_id)

    def start_all(self) -> None:
        for node in self._nodes.values():
            node.start()

    def stop_all(self) -> None:
        for node in self._nodes.values():
            node.stop()

    def active_nodes(self) -> list[NetworkNode]:
        return [
            node
            for node in self._nodes.values()
            if getattr(node, "state", None) == NodeState.ACTIVE
        ]

    def snapshot(self) -> dict[str, object]:
        return {
            node_id: (
                node.snapshot()
                if hasattr(node, "snapshot")
                else {"node_id": node_id}
            )
            for node_id, node in self._nodes.items()
        }
