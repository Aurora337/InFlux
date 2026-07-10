from __future__ import annotations

from .cluster import Cluster
from .cluster_member import ClusterMember
from .membership_policy import MembershipPolicy


class MembershipValidator:
    """
    Validates cluster membership operations.
    """


    def __init__(
        self,
        policy: MembershipPolicy,
    ) -> None:

        self.policy = policy


    def validate_join(
        self,
        cluster: Cluster,
        member: ClusterMember,
    ) -> bool:
        """
        Validate a member joining.
        """

        if member.node_id in cluster.members:
            return False


        if not self.policy.validate_member_limit(
            cluster.member_count()
        ):
            return False


        return self.policy.validate_roles(
            validator=member.validator,
            storage=member.storage,
            archive=member.archive,
        )


    def validate_leave(
        self,
        cluster: Cluster,
        node_id: str,
    ) -> bool:
        """
        Validate member removal.
        """

        return (
            node_id
            in cluster.members
        )