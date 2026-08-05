from __future__ import annotations

from dataclasses import dataclass, field

from .cluster import Cluster


@dataclass(slots=True)
class ClusterRegistry:
    """
    Deterministic registry of network clusters.
    """

    _clusters: dict[str, Cluster] = field(
        default_factory=dict
    )

    def register(
        self,
        cluster: Cluster,
    ) -> None:
        """
        Register a cluster.
        """

        self._clusters[
            cluster.cluster_id
        ] = cluster

    def unregister(
        self,
        cluster_id: str,
    ) -> None:
        """
        Remove a cluster.
        """

        self._clusters.pop(
            cluster_id,
            None,
        )

    def get(
        self,
        cluster_id: str,
    ) -> Cluster | None:
        """
        Retrieve a cluster.
        """

        return self._clusters.get(
            cluster_id
        )

    def exists(
        self,
        cluster_id: str,
    ) -> bool:
        """
        Determine whether a cluster exists.
        """

        return cluster_id in self._clusters

    def clusters(
        self,
    ) -> list[Cluster]:
        """
        Return clusters in deterministic order.
        """

        return sorted(
            self._clusters.values(),
            key=lambda cluster: cluster.cluster_id,
        )

    def count(
        self,
    ) -> int:
        """
        Number of registered clusters.
        """

        return len(
            self._clusters
        )

    def clear(
        self,
    ) -> None:
        """
        Remove every registered cluster.
        """

        self._clusters.clear()