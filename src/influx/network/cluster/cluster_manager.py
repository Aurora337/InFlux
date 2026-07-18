from __future__ import annotations

from dataclasses import dataclass

from .cluster import Cluster
from .cluster_member import ClusterMember
from .cluster_registry import ClusterRegistry
from .cluster_validator import ClusterValidator


@dataclass(slots=True)
class ClusterManager:
    """
    Deterministic cluster management service.
    """

    registry: ClusterRegistry
    validator: ClusterValidator

    def register(
        self,
        cluster: Cluster,
    ) -> bool:
        """
        Register a validated cluster.
        """

        if not self.validator.validate(cluster):
            return False

        self.registry.register(cluster)

        return True

    def unregister(
        self,
        cluster_id: str,
    ) -> None:
        """
        Remove a cluster.
        """

        self.registry.unregister(cluster_id)

    def get(
        self,
        cluster_id: str,
    ) -> Cluster | None:
        """
        Retrieve a registered cluster.
        """

        return self.registry.get(cluster_id)

    def add_member(
        self,
        cluster_id: str,
        member: ClusterMember,
    ) -> bool:
        """
        Add a member to a cluster.
        """

        cluster = self.registry.get(cluster_id)

        if cluster is None:
            return False

        cluster.add_member(member)

        return self.validator.validate(cluster)

    def remove_member(
        self,
        cluster_id: str,
        node_id: str,
    ) -> bool:
        """
        Remove a member from a cluster.
        """

        cluster = self.registry.get(cluster_id)

        if cluster is None:
            return False

        cluster.remove_member(node_id)

        return self.validator.validate(cluster)

    def clusters(
        self,
    ) -> list[Cluster]:
        """
        Return all registered clusters.
        """

        return self.registry.clusters()

    def count(
        self,
    ) -> int:
        """
        Return number of registered clusters.
        """

        return self.registry.count()

    def clear(
        self,
    ) -> None:
        """
        Remove all registered clusters.
        """

        self.registry.clear()