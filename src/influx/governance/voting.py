"""
Deterministic voting subsystem for InFlux governance.

Provides token-weighted voting with snapshot/block-height semantics,
vote power calculation, and replay-safe vote recording.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class VoteOption(Enum):
    """Canonical vote options."""

    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"
    VETO = "veto"


@dataclass(slots=True)
class VotingPower:
    """
    Encapsulates a voter's power at a specific snapshot block.

    This is deterministic: given the same state at the snapshot height,
    every node computes the same voting power.
    """

    voter_id: str
    power: float
    delegated_from: list[str] = field(default_factory=list)
    snapshot_block_height: int = 0

    def snapshot(self) -> dict[str, Any]:
        """Deterministic voting power snapshot."""
        return {
            "voter_id": self.voter_id,
            "power": self.power,
            "delegated_from": sorted(self.delegated_from),
            "snapshot_block_height": self.snapshot_block_height,
        }


@dataclass(slots=True)
class Vote:
    """
    A single vote cast on a proposal.

    Each vote is hashed deterministically for replay protection.
    """

    voter_id: str
    proposal_id: str
    option: VoteOption
    power: float
    timestamp: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic vote hash."""
        canonical = {
            "voter_id": self.voter_id,
            "proposal_id": self.proposal_id,
            "option": self.option.value,
            "power": self.power,
            "timestamp": self.timestamp,
        }
        serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def validate(self) -> bool:
        """Validate vote invariants."""
        if not self.voter_id:
            return False
        if not self.proposal_id:
            return False
        if self.power < 0:
            return False
        if self._hash is not None and self._hash != self.compute_hash():
            return False
        return True

    def snapshot(self) -> dict[str, Any]:
        """Deterministic vote snapshot."""
        return {
            "voter_id": self.voter_id,
            "proposal_id": self.proposal_id,
            "option": self.option.value,
            "power": self.power,
            "hash": self.hash,
        }


@dataclass(slots=True)
class VotingSession:
    """
    Manages a complete voting session for a single proposal.

    Handles:
    - Vote casting with power checks
    - Quorum calculation
    - Approval threshold evaluation
    - Deterministic result computation
    """

    proposal_id: str
    votes: dict[str, Vote] = field(default_factory=dict)
    voting_powers: dict[str, VotingPower] = field(default_factory=dict)
    start_block: int = 0
    end_block: int = 0
    quorum: float = 0.4
    approval_threshold: float = 0.5
    total_power_snapshot: float = 0.0

    def cast_vote(self, vote: Vote) -> bool:
        """
        Cast a vote on the proposal.

        Returns True if the vote is accepted.
        """
        # Check voter has power
        if vote.voter_id not in self.voting_powers:
            return False

        # Check vote power matches snapshot
        if vote.power != self.voting_powers[vote.voter_id].power:
            return False

        # Check no double voting
        if vote.voter_id in self.votes:
            return False

        # Validate the vote
        if not vote.validate():
            return False

        self.votes[vote.voter_id] = vote
        return True

    def has_quorum(self) -> bool:
        """Check if quorum is reached."""
        if self.total_power_snapshot <= 0:
            return False
        voted_power = sum(v.power for v in self.votes.values())
        return (voted_power / self.total_power_snapshot) >= self.quorum

    def get_approval(self) -> bool:
        """
        Check if the proposal passes approval threshold.

        Only considers YES and NO votes (ABSTAIN and VETO are excluded from denominator).
        """
        yes_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.YES)
        no_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.NO)

        total_yes_no = yes_power + no_power
        if total_yes_no <= 0:
            return False

        return (yes_power / total_yes_no) >= self.approval_threshold

    def has_veto(self) -> bool:
        """Check if superminority veto is triggered (default 1/3)."""
        total_voted = sum(v.power for v in self.votes.values())
        if total_voted <= 0:
            return False
        veto_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.VETO)
        # Superminority veto at 33.4%
        return (veto_power / total_voted) > (1 / 3)

    def compute_result(self) -> dict[str, Any]:
        """
        Compute the deterministic voting result.

        Returns:
            dict with: passed, yes_power, no_power, abstain_power, veto_power,
                       total_voted, quorum_reached, veto_active, approval
        """
        yes_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.YES)
        no_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.NO)
        abstain_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.ABSTAIN)
        veto_power = sum(v.power for v in self.votes.values() if v.option == VoteOption.VETO)
        total_voted = yes_power + no_power + abstain_power + veto_power

        quorum_reached = self.has_quorum()
        approval = self.get_approval()
        veto_active = self.has_veto()

        passed = quorum_reached and approval and not veto_active

        return {
            "passed": passed,
            "yes_power": yes_power,
            "no_power": no_power,
            "abstain_power": abstain_power,
            "veto_power": veto_power,
            "total_voted": total_voted,
            "total_power_snapshot": self.total_power_snapshot,
            "quorum_reached": quorum_reached,
            "veto_active": veto_active,
            "approval": approval,
            "voter_count": len(self.votes),
        }

    def register_voting_power(self, voter_id: str, power: float, delegated: Optional[list[str]] = None) -> bool:
        """Register voting power for a voter at the snapshot block."""
        if voter_id in self.voting_powers:
            return False
        self.voting_powers[voter_id] = VotingPower(
            voter_id=voter_id,
            power=power,
            delegated_from=delegated or [],
            snapshot_block_height=self.start_block,
        )
        return True

    def snapshot(self) -> dict[str, Any]:
        """Deterministic voting session snapshot."""
        return {
            "proposal_id": self.proposal_id,
            "vote_count": len(self.votes),
            "voter_count": len(self.voting_powers),
            "start_block": self.start_block,
            "end_block": self.end_block,
            "quorum": self.quorum,
            "approval_threshold": self.approval_threshold,
            "total_power_snapshot": self.total_power_snapshot,
            "result": self.compute_result(),
        }
