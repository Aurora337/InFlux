from __future__ import annotations

from typing import Dict, Optional

from .cluster import Cluster
from .cluster_member import ClusterMember
from .cluster_metrics import ClusterMetrics
from .leader import Leader
from .leader_election import LeaderElection
from .membership import Membership


class ClusterManager:
    """
    Coordinates cluster operations.
    """


    def __init__(
        self,
    ) -> None:

        self.clusters: Dict[
            str,
            Cluster,
        ] = {}

        self.membership = Membership()

        self.election = LeaderElection()

        self.metrics = ClusterMetrics()

        self.leaders: Dict[
            str,
            Leader,
        ] = {}


    def register(
        self,
        cluster: Cluster,
    ) -> None:
        """
        Register cluster.
        """

        self.clusters[
            cluster.cluster_id
        ] = cluster


    def lookup(
        self,
        cluster_id: str,
    ) -> Optional[Cluster]:
        """
        Find cluster.
        """

        return self.clusters.get(
            cluster_id
        )


    def join(
        self,
        cluster_id: str,
        member: ClusterMember,
    ) -> bool:
        """
        Add member to cluster.
        """

        cluster = self.lookup(
            cluster_id
        )

        if cluster is None:
            return False


        result = self.membership.join(
            cluster,
            member,
        )


        if result:
            self.metrics.record_join()


        return result


    def elect_leader(
        self,
        cluster_id: str,
    ) -> Leader | None:
        """
        Elect cluster leader.
        """

        cluster = self.lookup(
            cluster_id
        )

        if cluster is None:
            return None


        leader = self.election.elect(
            cluster
        )


        if leader is not None:

            self.leaders[
                cluster_id
            ] = leader

            self.metrics.record_election()


        return leader


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic manager snapshot.
        """

        return {
            "clusters": {
                name:
                    cluster.snapshot()

                for name, cluster
                in self.clusters.items()
            },

            "leaders": {
                name:
                    leader.snapshot()

                for name, leader
                in self.leaders.items()
            },

            "metrics":
                self.metrics.snapshot(),
        }