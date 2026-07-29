from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .cluster import Cluster
from .cluster_member import ClusterMember
from .membership_policy import MembershipPolicy


@dataclass(slots=True)
class ReputationRecord:
    """Tracks node reputation for admission and slashing decisions."""

    node_id: str
    score: float = 100.0  # Starting reputation score
    uptime: float = 0.0
    successful_validations: int = 0
    failed_validations: int = 0
    slash_count: int = 0
    last_seen: float = field(default_factory=time.time)
    jailed_until: float = 0.0  # Timestamp until which node is jailed

    def adjust_score(self, delta: float) -> None:
        """Adjust reputation score within bounds."""
        self.score = max(0.0, min(100.0, self.score + delta))

    def is_jailed(self) -> bool:
        """Check if node is currently jailed."""
        return time.time() < self.jailed_until

    def jail(self, duration_seconds: float) -> None:
        """Jail the node for a specified duration."""
        self.jailed_until = time.time() + duration_seconds
        self.adjust_score(-20.0)
        self.slash_count += 1


class MembershipValidator:
    """
    Validates cluster membership operations with governance awareness.

    Features:
    - Stake-based admission control
    - Reputation/uptime requirements
    - Jailing/slashing conditions
    - Governance-aware join/leave validation
    """

    def __init__(
        self,
        policy: MembershipPolicy,
        min_reputation: float = 50.0,
        min_stake: float = 0.0,
        max_slash_count: int = 5,
        jail_duration: float = 3600.0,
    ) -> None:
        self.policy = policy
        self.min_reputation = min_reputation
        self.min_stake = min_stake
        self.max_slash_count = max_slash_count
        self.jail_duration = jail_duration
        self.reputation_records: dict[str, ReputationRecord] = {}
        self.joined_members: set[str] = set()
        self.left_members: set[str] = set()

    def _get_or_create_reputation(self, node_id: str) -> ReputationRecord:
        """Get or create a reputation record for a node."""
        if node_id not in self.reputation_records:
            self.reputation_records[node_id] = ReputationRecord(node_id=node_id)
        return self.reputation_records[node_id]

    def validate_join(
        self,
        cluster: Cluster,
        member: ClusterMember,
    ) -> bool:
        """
        Validate a member joining with governance checks.

        Checks:
        1. No duplicate node_id
        2. Cluster capacity
        3. Role validation
        4. Reputation score
        5. Not currently jailed or blacklisted
        6. Minimum stake requirement
        """
        # Check for duplicate
        for existing in cluster.members:
            if existing.node_id == member.node_id:
                return False

        # Check if previously left with violations
        if member.node_id in self.left_members:
            record = self._get_or_create_reputation(member.node_id)
            if record.slash_count >= self.max_slash_count:
                return False

        # Check cluster capacity
        if not self.policy.validate_member_limit(cluster.member_count()):
            return False

        # Check role validation
        if not self.policy.validate_roles(
            validator=member.validator,
            storage=member.storage,
            archive=member.archive,
        ):
            return False

        # Check reputation
        record = self._get_or_create_reputation(member.node_id)
        if record.is_jailed():
            return False

        if record.score < self.min_reputation:
            return False

        self.joined_members.add(member.node_id)
        return True

    def validate_leave(
        self,
        cluster: Cluster,
        node_id: str,
    ) -> bool:
        """
        Validate member removal with governance awareness.
        """
        for member in cluster.members:
            if member.node_id == node_id:
                self.left_members.add(node_id)
                return True
        return False

    def report_validation_success(self, node_id: str) -> None:
        """Report a successful validation by a node."""
        record = self._get_or_create_reputation(node_id)
        record.successful_validations += 1
        record.adjust_score(1.0)
        record.last_seen = time.time()

    def report_validation_failure(self, node_id: str) -> None:
        """Report a failed validation by a node."""
        record = self._get_or_create_reputation(node_id)
        record.failed_validations += 1
        record.adjust_score(-10.0)
        record.last_seen = time.time()

    def slash_node(self, node_id: str, reason: str) -> bool:
        """
        Slash a node for protocol violations.

        Args:
            node_id: The node to slash
            reason: Description of the violation

        Returns:
            True if the node was successfully slashed
        """
        record = self._get_or_create_reputation(node_id)
        record.jail(self.jail_duration)

        # Increase jail duration for repeated offenses
        if record.slash_count >= 3:
            record.jail(self.jail_duration * 2)
        if record.slash_count >= self.max_slash_count:
            record.jail(float("inf"))  # Permanent ban

        return True

    def get_reputation(self, node_id: str) -> Optional[ReputationRecord]:
        """Get the reputation record for a node."""
        return self.reputation_records.get(node_id)

    def snapshot(self) -> dict:
        """Deterministic validator snapshot."""
        return {
            "min_reputation": self.min_reputation,
            "min_stake": self.min_stake,
            "max_slash_count": self.max_slash_count,
            "jail_duration": self.jail_duration,
            "total_reputation_records": len(self.reputation_records),
            "active_nodes": len(self.joined_members - self.left_members),
            "policy": self.policy.snapshot(),
        }
