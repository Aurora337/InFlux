from __future__ import annotations

from dataclasses import dataclass

from .cluster import Cluster


@dataclass(slots=True)
class ClusterValidator:
    """
    Validates deterministic cluster integrity.
    """

    def validate(
        self,
        cluster: Cluster,
    ) -> bool:
        """
        Validate a cluster.
        """

        try:
            cluster.config.validate()
        except ValueError:
            return False

        members = cluster.members

        if len(members) < cluster.config.min_members:
            return False

        if len(members) > cluster.config.max_members:
            return False

        node_ids: set[str] = set()

        for member in members:
            try:
                member.validate()
            except ValueError:
                return False

            if member.node_id in node_ids:
                return False

            node_ids.add(
                member.node_id
            )

        return True