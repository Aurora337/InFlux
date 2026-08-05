from __future__ import annotations

from .cluster import Cluster
from .leader import Leader


class LeaderElection:
    """
    Deterministic leader election.

    Uses ordered node identifiers to ensure
    every node reaches the same decision.
    """


    def elect(
        self,
        cluster: Cluster,
    ) -> Leader | None:
        """
        Select leader.
        """

        active_members = sorted(
            [
                member.node_id
                for member in cluster.members
                if member.active
            ]
        )


        if not active_members:
            return None


        return Leader(
            node_id=active_members[0]
        )