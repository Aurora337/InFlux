from __future__ import annotations

from dataclasses import dataclass

from .registry import (
    PeerRecord,
    PeerRegistry,
)


@dataclass(frozen=True, slots=True)
class BootstrapNode:
    """
    Represents a trusted bootstrap node.
    """

    node_id: str

    address: str

    port: int


class BootstrapManager:
    """
    Manages network bootstrap discovery.
    """

    def __init__(
        self,
        registry: PeerRegistry,
    ) -> None:

        self._registry = registry

        self._bootstrap_nodes: list[
            BootstrapNode
        ] = []

    def add_bootstrap_node(
        self,
        node: BootstrapNode,
    ) -> None:
        """
        Add bootstrap node.
        """

        self._bootstrap_nodes.append(
            node
        )

        self._registry.register(
            PeerRecord(
                node_id=node.node_id,
                address=node.address,
                port=node.port,
            )
        )

    def bootstrap_nodes(
        self,
    ) -> list[BootstrapNode]:
        """
        Return known bootstrap nodes.
        """

        return list(
            self._bootstrap_nodes
        )

    def discover(
        self,
    ) -> list[PeerRecord]:
        """
        Return discovered peers.
        """

        return self._registry.list_peers()