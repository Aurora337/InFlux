from __future__ import annotations

from typing import Dict, Optional

from .cluster_member import ClusterMember
from .cluster_state import ClusterState


class Cluster:
    """
    Represents a coordinated group of nodes.
    """


    def __init__(
        self,
        cluster_id: str,
    ) -> None:

        self.cluster_id = cluster_id

        self.members: Dict[
            str,
            ClusterMember,
        ] = {}

        self.state = ClusterState.INITIALIZING


    def form(
        self,
    ) -> None:
        """
        Begin cluster formation.
        """

        self.state = ClusterState.FORMING


    def activate(
        self,
    ) -> None:
        """
        Activate cluster.
        """

        self.state = ClusterState.ACTIVE


    def add_member(
        self,
        member: ClusterMember,
    ) -> bool:
        """
        Add member to cluster.
        """

        if member.node_id in self.members:
            return False

        self.members[
            member.node_id
        ] = member

        return True


    def remove_member(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove member.
        """

        if node_id not in self.members:
            return False

        del self.members[
            node_id
        ]

        return True


    def lookup(
        self,
        node_id: str,
    ) -> Optional[ClusterMember]:
        """
        Find cluster member.
        """

        return self.members.get(
            node_id
        )


    def member_count(
        self,
    ) -> int:
        """
        Return number of members.
        """

        return len(
            self.members
        )


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic cluster snapshot.
        """

        return {
            "cluster_id":
                self.cluster_id,

            "state":
                self.state.value,

            "members": {
                node_id:
                    member.snapshot()

                for node_id, member
                in self.members.items()
            },
        }