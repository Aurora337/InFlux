from __future__ import annotations

from dataclasses import dataclass, field

from .cluster_config import ClusterConfig
from .cluster_member import ClusterMember
from .cluster_state import ClusterState


@dataclass(slots=True)
class Cluster:
    """
    Deterministic network cluster.
    """

    cluster_id: str

    config: ClusterConfig = field(
        default_factory=ClusterConfig
    )

    state: ClusterState = ClusterState.INITIALIZING

    members: list[ClusterMember] = field(
        default_factory=list
    )

    def form(
        self,
    ) -> bool:
        """
        Transition to forming state.
        """

        self.state = ClusterState.FORMING
        return True

    def activate(
        self,
    ) -> bool:
        """
        Transition to active state.
        """

        self.state = ClusterState.ACTIVE
        return True

    def add_member(
        self,
        member: ClusterMember,
    ) -> bool:
       """
       Add a cluster member.
       """

       if len(self.members) >= self.config.max_members:
           raise ValueError(
            "cluster capacity reached"
        )

       if member in self.members:
            return False

       self.members.append(member)
       return True

    def lookup(
        self,
        node_id: str,
    ) -> ClusterMember | None:
        """
        Lookup a member by node ID.
        """

        for member in self.members:
            if member.node_id == node_id:
                return member

        return None

    def remove_member(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove a cluster member.
        """

        for member in self.members:
            if member.node_id == node_id:
                self.members.remove(member)
                return True

        return False

    def member_count(
        self,
    ) -> int:
        """
        Return number of members.
        """

        return len(self.members)

    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic cluster snapshot.
        """

        return {
            "cluster_id": self.cluster_id,
            "state": self.state.value,
            "member_count": len(self.members),
        }