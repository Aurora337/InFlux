from __future__ import annotations

from .cluster import Cluster
from .cluster_member import ClusterMember
from .membership_policy import MembershipPolicy
from .membership_validator import MembershipValidator


class Membership:
    """
    Coordinates cluster membership changes.
    """


    def __init__(
        self,
        policy: MembershipPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else MembershipPolicy()
        )

        self.validator = MembershipValidator(
            self.policy
        )


    def join(
        self,
        cluster: Cluster,
        member: ClusterMember,
    ) -> bool:
        """
        Add member to cluster.
        """

        if not self.validator.validate_join(
            cluster,
            member,
        ):
            return False


        return cluster.add_member(
            member
        )


    def leave(
        self,
        cluster: Cluster,
        node_id: str,
    ) -> bool:
        """
        Remove member from cluster.
        """

        if not self.validator.validate_leave(
            cluster,
            node_id,
        ):
            return False


        return cluster.remove_member(
            node_id
        )