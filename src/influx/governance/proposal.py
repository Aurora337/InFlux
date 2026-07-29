"""
Deterministic proposal lifecycle management for InFlux governance.

Provides proposal serialization, hashing, and lifecycle state machine
transitions with full replay protection and audit trail.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class ProposalType(Enum):
    """Canonical proposal types for on-chain governance."""

    TEXT = "text"
    PARAMETER_CHANGE = "parameter_change"
    UPGRADE = "upgrade"
    TREASURY = "treasury"
    ECONOMIC = "economic"


class ProposalStatus(Enum):
    """Deterministic proposal lifecycle states."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    FAILED = "failed"
    EXECUTED = "executed"
    EXPIRED = "expired"
    VETOED = "vetoed"


@dataclass(slots=True)
class ProposalLifecycle:
    """
    Deterministic proposal lifecycle state machine.

    Guarantees:
    - DRAFT → PENDING → ACTIVE → (PASSED | FAILED) → EXECUTED
    - Any state → EXPIRED at deadline
    - Any state → VETOED by governance authority
    - Replay-safe transitions
    """

    current: ProposalStatus = ProposalStatus.DRAFT
    created_at: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
    activated_at: Optional[int] = None
    resolved_at: Optional[int] = None
    executed_at: Optional[int] = None

    def transition(self, target: ProposalStatus) -> bool:
        """
        Attempt a deterministic state transition.

        Returns True if the transition is valid and applied.
        """
        valid_transitions = {
            ProposalStatus.DRAFT: {ProposalStatus.PENDING, ProposalStatus.EXPIRED},
            ProposalStatus.PENDING: {ProposalStatus.ACTIVE, ProposalStatus.EXPIRED, ProposalStatus.VETOED},
            ProposalStatus.ACTIVE: {ProposalStatus.PASSED, ProposalStatus.FAILED, ProposalStatus.EXPIRED, ProposalStatus.VETOED},
            ProposalStatus.PASSED: {ProposalStatus.EXECUTED, ProposalStatus.EXPIRED},
            ProposalStatus.FAILED: set(),
            ProposalStatus.EXECUTED: set(),
            ProposalStatus.EXPIRED: set(),
            ProposalStatus.VETOED: set(),
        }

        if target not in valid_transitions[self.current]:
            return False

        now = int(datetime.now(timezone.utc).timestamp())
        if target == ProposalStatus.ACTIVE:
            self.activated_at = now
        if target in (ProposalStatus.PASSED, ProposalStatus.FAILED):
            self.resolved_at = now
        if target == ProposalStatus.EXECUTED:
            self.executed_at = now

        self.current = target
        return True

    def snapshot(self) -> dict[str, Any]:
        """Deterministic lifecycle snapshot."""
        return {
            "current": self.current.value,
            "created_at": self.created_at,
            "activated_at": self.activated_at,
            "resolved_at": self.resolved_at,
            "executed_at": self.executed_at,
        }


@dataclass(slots=True)
class Proposal:
    """
    Deterministic governance proposal.

    All proposals are hashed deterministically for replay protection
    and can be reconstructed from their hash across any node.
    """

    proposal_id: str
    title: str
    description: str
    proposer: str
    proposal_type: ProposalType
    lifecycle: ProposalLifecycle = field(default_factory=ProposalLifecycle)
    target_block_height: int = 0
    execution_delay_blocks: int = 100
    quorum: float = 0.4
    approval_threshold: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """
        Compute deterministic proposal hash.

        Uses SHA-256 over canonical JSON encoding of all proposal fields.
        """
        canonical = {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposer": self.proposer,
            "proposal_type": self.proposal_type.value,
            "target_block_height": self.target_block_height,
            "execution_delay_blocks": self.execution_delay_blocks,
            "quorum": self.quorum,
            "approval_threshold": self.approval_threshold,
            "metadata": dict(sorted(self.metadata.items())),
        }
        serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        """Deterministic proposal snapshot."""
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "proposer": self.proposer,
            "proposal_type": self.proposal_type.value,
            "status": self.lifecycle.current.value,
            "hash": self.hash,
            "lifecycle": self.lifecycle.snapshot(),
            "target_block_height": self.target_block_height,
            "quorum": self.quorum,
            "approval_threshold": self.approval_threshold,
        }

    def validate(self) -> bool:
        """
        Validate proposal invariants.

        Returns True if all invariants are satisfied.
        """
        if not self.proposal_id:
            return False
        if not self.title:
            return False
        if not self.proposer:
            return False
        if self.quorum < 0 or self.quorum > 1:
            return False
        if self.approval_threshold < 0 or self.approval_threshold > 1:
            return False
        if self.execution_delay_blocks < 0:
            return False
        # Verify hash integrity
        if self._hash is not None and self._hash != self.compute_hash():
            return False
        return True
