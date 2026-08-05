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

        for existing in cluster.members:
            if existing.node_id == member.node_id:
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

        for member in cluster.members:
            if member.node_id == node_id:
                return True

        return False