"""
Governance metrics collection for InFlux.

Tracks proposal throughput, voting participation, governance cycle time,
and treasury health metrics with deterministic snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class GovernanceMetrics:
    """
    Collects and reports governance metrics.

    All metrics are recorded deterministically and can be
    snapshotted for dashboard display and audit purposes.
    """

    proposals_created: int = 0
    proposals_submitted: int = 0
    proposals_activated: int = 0
    proposals_passed: int = 0
    proposals_approved: int = 0
    proposals_failed: int = 0
    proposals_rejected: int = 0
    proposals_executed: int = 0
    proposals_expired: int = 0
    proposals_vetoed: int = 0
    votes_cast: int = 0
    total_voting_power: float = 0.0
    governance_cycle_time_blocks: int = 0
    treasury_balance_influx: float = 0.0
    total_dispersed: float = 0.0
    total_deposited: float = 0.0
    upgrades_activated: int = 0
    approvals_recorded: int = 0

    def record_proposal(self) -> None:
        """Record a created governance proposal."""
        self.proposals_created += 1

    def record_proposal_created(self) -> None:
        """Record a proposal creation event."""
        self.proposals_created += 1

    def record_proposal_submitted(self) -> None:
        """Record a proposal submission event."""
        self.proposals_submitted += 1

    def record_proposal_activated(self) -> None:
        """Record a proposal activation event."""
        self.proposals_activated += 1

    def record_proposal_passed(self) -> None:
        """Record a proposal passing event."""
        self.proposals_passed += 1

    def record_proposal_failed(self) -> None:
        """Record a proposal failure event."""
        self.proposals_failed += 1

    def record_proposal_executed(self) -> None:
        """Record a proposal execution event."""
        self.proposals_executed += 1

    def record_vote(self) -> None:
        """Compatibility wrapper for vote recording."""
        self.record_vote_cast()

    def record_vote_cast(self) -> None:
        """Record a vote cast event."""
        self.votes_cast += 1

    def record_approval(self) -> None:
        """Record a governance approval event."""
        self.approvals_recorded += 1
        self.proposals_approved += 1
        self.proposals_passed +=1

    def record_rejection(self) -> None:
        """Record a governance rejection event."""
        self.proposals_failed += 1
        self.proposals_rejected += 1

    def record_upgrade(self) -> None:
        """Record a governance upgrade activation event."""
        self.upgrades_activated += 1

    def compute_voting_participation_rate(self) -> float:
        """Compute the voting participation rate."""
        total_proposals = self.proposals_activated
        if total_proposals == 0:
            return 0.0
        total_voted = self.proposals_passed + self.proposals_failed
        return total_voted / total_proposals

    def compute_proposal_success_rate(self) -> float:
        """Compute the proposal success rate."""
        total_resolved = self.proposals_passed + self.proposals_failed
        if total_resolved == 0:
            return 0.0
        return self.proposals_passed / total_resolved

    def snapshot(self) -> dict[str, Any]:
        """Deterministic metrics snapshot."""
        return {
            "upgrades_activated": self.upgrades_activated,
            "approvals_recorded": self.approvals_recorded,
            "proposals_created": self.proposals_created,
            "proposals_submitted": self.proposals_submitted,
            "proposals_activated": self.proposals_activated,
            "proposals_passed": self.proposals_passed,
            "proposals_failed": self.proposals_failed,
            "proposals_executed": self.proposals_executed,
            "proposals_expired": self.proposals_expired,
            "proposals_vetoed": self.proposals_vetoed,
            "votes_cast": self.votes_cast,
            "total_voting_power": self.total_voting_power,
            "voting_participation_rate": self.compute_voting_participation_rate(),
            "proposal_success_rate": self.compute_proposal_success_rate(),
            "treasury_balance_influx": self.treasury_balance_influx,
            "total_dispersed": self.total_dispersed,
            "total_deposited": self.total_deposited,
        }
