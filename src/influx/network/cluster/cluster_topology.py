from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ClusterTopology:
    """
    Tracks deterministic cluster topology.
    """

    _neighbors: dict[str, set[str]] = field(
        default_factory=dict
    )

    def connect(
        self,
        node_a: str,
        node_b: str,
    ) -> None:
        """
        Create a bidirectional connection.
        """

        self._neighbors.setdefault(node_a, set()).add(node_b)
        self._neighbors.setdefault(node_b, set()).add(node_a)

    def disconnect(
        self,
        node_a: str,
        node_b: str,
    ) -> None:
        """
        Remove a bidirectional connection.
        """

        self._neighbors.get(node_a, set()).discard(node_b)
        self._neighbors.get(node_b, set()).discard(node_a)

    def neighbors(
        self,
        node_id: str,
    ) -> set[str]:
        """
        Return neighboring nodes.
        """

        return set(self._neighbors.get(node_id, set()))

    def snapshot(
        self,
    ) -> dict[str, list[str]]:
        """
        Deterministic topology snapshot.
        """

        return {
            node: sorted(peers)
            for node, peers in self._neighbors.items()
        }