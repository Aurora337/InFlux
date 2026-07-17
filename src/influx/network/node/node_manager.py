from __future__ import annotations

from dataclasses import dataclass, field

from .network_node import NetworkNode


@dataclass(slots=True)
class NodeManager:
    """
    Deterministic manager for network nodes.
    """

    _nodes: dict[str, NetworkNode] = field(
        default_factory=dict
    )

    def register(
        self,
        node: NetworkNode,
    ) -> None:
        self._nodes[node.node_id] = node

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