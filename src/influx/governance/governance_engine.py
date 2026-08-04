"""
Deterministic governance engine for InFlux.

Coordinates the full governance lifecycle including proposal management,
voting sessions, treasury interactions, and state transitions.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from influx.governance.proposal import (
    Proposal,
    ProposalStatus,
    ProposalType,
    ProposalLifecycle,
)
from influx.governance.voting import (
    Vote,
    VoteOption,
    VotingSession,
)
from influx.governance.treasury import Treasury
from influx.governance.governance_metrics import GovernanceMetrics
from influx.governance.drift_detector import DriftDetector


@dataclass(slots=True)
class GovernanceEngine:
    """
    Central governance coordinator for InFlux.

    Manages:
    - Proposal lifecycle (create, activate, resolve, execute)
    - Voting sessions (open, cast, tally, close)
    - Treasury interactions (dispersal creation, execution)
    - Governance metrics collection
    - Drift detection integration
    - Deterministic state transitions
    """

    proposals: dict[str, Proposal] = field(default_factory=dict)
    voting_sessions: dict[str, VotingSession] = field(default_factory=dict)
    treasury: Treasury = field(default_factory=Treasury)
    metrics: GovernanceMetrics = field(default_factory=GovernanceMetrics)
    drift_detector: DriftDetector = field(default_factory=DriftDetector)
    current_block_height: int = 0
    voting_period_blocks: int = 1000
    execution_delay_blocks: int = 100
    engine_id: str = field(default_factory=lambda: hashlib.sha256(
        f"governance-engine-{datetime.now(timezone.utc).timestamp()}".encode()
    ).hexdigest()[:16])

    def create_proposal(
        self,
        title: str,
        description: str,
        proposer: str,
        proposal_type: ProposalType = ProposalType.TEXT,
        target_block_height: int = 0,
        quorum: float = 0.4,
        approval_threshold: float = 0.5,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Proposal]:
        """
        Create a new governance proposal.

        Returns:
            Proposal if created successfully, None if validation fails.
        """
        if not title or not description or not proposer:
            return None

        proposal_id = hashlib.sha256(
            f"{proposer}:{title}:{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]

        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.DRAFT)

        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposer=proposer,
            proposal_type=proposal_type,
            lifecycle=lifecycle,
            target_block_height=target_block_height if target_block_height > 0 else self.current_block_height + 1,
            execution_delay_blocks=self.execution_delay_blocks,
            quorum=quorum,
            approval_threshold=approval_threshold,
            metadata=metadata or {},
        )

        if not proposal.validate():
            return None

        self.proposals[proposal_id] = proposal
        self.metrics.record_proposal_created()
        return proposal

    def submit_proposal(self, proposal_id: str) -> bool:
        """
        Submit a draft proposal for voting (transition DRAFT -> PENDING).

        Args:
            proposal_id: The proposal to submit

        Returns:
            True if successfully submitted
        """
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        if not proposal.lifecycle.transition(ProposalStatus.PENDING):
            return False

        self.metrics.record_proposal_submitted()
        return True

    def activate_proposal(self, proposal_id: str) -> bool:
        """
        Activate a proposal for voting (transition PENDING -> ACTIVE).

        Args:
            proposal_id: The proposal to activate

        Returns:
            True if successfully activated
        """
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        if not proposal.lifecycle.transition(ProposalStatus.ACTIVE):
            return False

        # Create voting session
        session = VotingSession(
            proposal_id=proposal_id,
            start_block=self.current_block_height,
            end_block=self.current_block_height + self.voting_period_blocks,
            quorum=proposal.quorum,
            approval_threshold=proposal.approval_threshold,
        )
        self.voting_sessions[proposal_id] = session
        self.metrics.record_proposal_activated()
        return True

    def cast_vote(self, proposal_id: str, voter_id: str, option: VoteOption,
                   power: float) -> bool:
        """
        Cast a vote on an active proposal.

        Args:
            proposal_id: The proposal to vote on
            voter_id: The voter's identifier
            option: The vote option (YES, NO, ABSTAIN, VETO)
            power: The voting power (must match registered power)

        Returns:
            True if vote was accepted
        """
        if proposal_id not in self.proposals:
            return False
        if proposal_id not in self.voting_sessions:
            return False

        proposal = self.proposals[proposal_id]
        if proposal.lifecycle.current != ProposalStatus.ACTIVE:
            return False

        session = self.voting_sessions[proposal_id]

        # Register voting power if not already registered
        if voter_id not in session.voting_powers:
            session.register_voting_power(voter_id, power)

        vote = Vote(
            voter_id=voter_id,
            proposal_id=proposal_id,
            option=option,
            power=power,
        )

        success = session.cast_vote(vote)
        if success:
            self.metrics.record_vote_cast()
        return success

    def close_voting(self, proposal_id: str) -> bool:
        """
        Close voting on a proposal and determine result.

        Args:
            proposal_id: The proposal to close

        Returns:
            True if voting was closed and proposal resolved
        """
        if proposal_id not in self.proposals:
            return False
        if proposal_id not in self.voting_sessions:
            return False

        proposal = self.proposals[proposal_id]
        session = self.voting_sessions[proposal_id]

        if proposal.lifecycle.current != ProposalStatus.ACTIVE:
            return False

        result = session.compute_result()

        if result["passed"]:
            proposal.lifecycle.transition(ProposalStatus.PASSED)
            self.metrics.record_proposal_passed()
        else:
            proposal.lifecycle.transition(ProposalStatus.FAILED)
            self.metrics.record_proposal_failed()

        return True

    def execute_proposal(self, proposal_id: str) -> bool:
        """
        Execute a passed proposal.

        Args:
            proposal_id: The proposal to execute

        Returns:
            True if successfully executed
        """
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        if proposal.lifecycle.current != ProposalStatus.PASSED:
            return False

        # Check execution delay
        if self.current_block_height < proposal.target_block_height + proposal.execution_delay_blocks:
            return False

        result = proposal.lifecycle.transition(ProposalStatus.EXECUTED)
        if result:
            self.metrics.record_proposal_executed()

            # Handle treasury proposals
            if proposal.proposal_type == ProposalType.TREASURY:
                dispersal_amount = proposal.metadata.get("amount", 0)
                recipient = proposal.metadata.get("recipient", "")
                token = proposal.metadata.get("token", "INFLUX")
                if dispersal_amount > 0 and recipient:
                    dispersal = self.treasury.create_dispersal(
                        proposal_id=proposal_id,
                        recipient=recipient,
                        amount=dispersal_amount,
                        token=token,
                        reason=proposal.title,
                    )
                    if dispersal:
                        self.treasury.approve_dispersal(dispersal.dispersal_id)
                        self.treasury.execute_dispersal(dispersal.dispersal_id)

            # Run drift detection
            self.drift_detector.check_all()

        return result

    def advance_block(self) -> None:
        """
        Advance the current block height.

        Called at each block to:
        - Update block height
        - Auto-close expired voting sessions
        - Auto-execute eligible proposals
        """
        self.current_block_height += 1

        # Check for expired voting sessions
        for proposal_id in list(self.voting_sessions.keys()):
            if proposal_id not in self.proposals:
                continue
            proposal = self.proposals[proposal_id]
            if proposal.lifecycle.current != ProposalStatus.ACTIVE:
                continue
            session = self.voting_sessions[proposal_id]
            if self.current_block_height >= session.end_block:
                self.close_voting(proposal_id)

        # Check for executable proposals
        for proposal_id in list(self.proposals.keys()):
            proposal = self.proposals[proposal_id]
            if proposal.lifecycle.current == ProposalStatus.PASSED:
                self.execute_proposal(proposal_id)

    def snapshot(self) -> dict[str, Any]:
        """Deterministic governance engine snapshot."""
        return {
            "engine_id": self.engine_id,
            "current_block_height": self.current_block_height,
            "proposal_count": len(self.proposals),
            "active_proposals": sum(
                1 for p in self.proposals.values()
                if p.lifecycle.current == ProposalStatus.ACTIVE
            ),
            "passed_proposals": sum(
                1 for p in self.proposals.values()
                if p.lifecycle.current == ProposalStatus.PASSED
            ),
            "executed_proposals": sum(
                1 for p in self.proposals.values()
                if p.lifecycle.current == ProposalStatus.EXECUTED
            ),
            "treasury": self.treasury.snapshot(),
            "metrics": self.metrics.snapshot(),
        }
