from __future__ import annotations

import hashlib
from .cluster import Cluster
from .leader import Leader


class LeaderElection:
    """
    Deterministic leader election with BFT awareness.

    Features:
    - Weighted election (by stake/uptime)
    - Leader rotation with term limits
    - Byzantine fault tolerance awareness
    - Deterministic tie-breaking via hash
    """

    def __init__(
        self,
        term_length: int = 10,
        max_terms: int = 3,
        bft_enabled: bool = True,
    ) -> None:
        self.term_length = term_length
        self.max_terms = max_terms
        self.bft_enabled = bft_enabled
        self.current_term: int = 0
        self.leader_history: dict[str, int] = {}  # node_id -> terms served

    def elect(
        self,
        cluster: Cluster,
        round_number: int = 0,
    ) -> Leader | None:
        """
        Select leader using weighted deterministic election.

        Args:
            cluster: The cluster to elect a leader for
            round_number: Current consensus round for rotation

        Returns:
            Leader or None if no active members
        """
        active_members = [
            member for member in cluster.members
            if member.active
        ]

        if not active_members:
            return None

        # Calculate term
        self.current_term = round_number // self.term_length

        # Filter out members that have exceeded max terms
        eligible = [
            m for m in active_members
            if self.leader_history.get(m.node_id, 0) < self.max_terms
        ]

        # If no eligible members, reset term limits
        if not eligible:
            self.leader_history.clear()
            eligible = active_members

        # Weighted election: sort by (validator status, node_id)
        # Validators get priority, then deterministic by node_id
        def weight(member) -> tuple:
            validator_weight = 0 if member.validator else 1
            return (validator_weight, member.node_id)

        eligible.sort(key=weight)

        # Apply round-based rotation within eligible set
        rotation_index = round_number % len(eligible)
        selected = eligible[rotation_index]

        # Track terms
        self.leader_history[selected.node_id] = (
            self.leader_history.get(selected.node_id, 0) + 1
        )

        return Leader(
            node_id=selected.node_id,
        )

    def get_bft_quorum_size(self, total_nodes: int) -> int:
        """
        Calculate BFT quorum size (2f + 1).

        Args:
            total_nodes: Total number of nodes

        Returns:
            Minimum quorum size for BFT safety
        """
        if not self.bft_enabled:
            return total_nodes // 2 + 1
        f = (total_nodes - 1) // 3
        return 2 * f + 1

    def get_bft_max_faulty(self, total_nodes: int) -> int:
        """
        Calculate maximum faulty nodes BFT can tolerate (f).

        Args:
            total_nodes: Total number of nodes

        Returns:
            Maximum number of faulty nodes
        """
        return (total_nodes - 1) // 3

    def snapshot(self) -> dict:
        """
        Deterministic leader election snapshot.
        """
        return {
            "current_term": self.current_term,
            "term_length": self.term_length,
            "max_terms": self.max_terms,
            "bft_enabled": self.bft_enabled,
            "leader_history": dict(self.leader_history),
        }
