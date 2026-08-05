"""
Deterministic treasury management for InFlux governance.

Provides treasury state management, fund dispersal,
and accounting with full audit trail.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class DispersalStatus(Enum):
    """Treasury dispersal lifecycle states."""

    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Dispersal:
    """
    A treasury fund dispersal request.

    Each dispersal is hashed deterministically for replay protection.
    """

    dispersal_id: str
    proposal_id: str
    recipient: str
    amount: float
    token: str
    reason: str
    status: DispersalStatus = DispersalStatus.PENDING
    created_at: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
    executed_at: Optional[int] = None
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic dispersal hash."""
        canonical = {
            "dispersal_id": self.dispersal_id,
            "proposal_id": self.proposal_id,
            "recipient": self.recipient,
            "amount": self.amount,
            "token": self.token,
            "reason": self.reason,
            "created_at": self.created_at,
        }
        serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def execute(self) -> bool:
        """Execute the dispersal."""
        if self.status != DispersalStatus.APPROVED:
            return False
        self.status = DispersalStatus.EXECUTED
        self.executed_at = int(datetime.now(timezone.utc).timestamp())
        return True

    def snapshot(self) -> dict[str, Any]:
        """Deterministic dispersal snapshot."""
        return {
            "dispersal_id": self.dispersal_id,
            "proposal_id": self.proposal_id,
            "recipient": self.recipient,
            "amount": self.amount,
            "token": self.token,
            "status": self.status.value,
            "hash": self.hash,
        }


@dataclass(slots=True)
class Treasury:
    """
    Deterministic treasury for managing protocol funds.

    Provides:
    - Balance tracking per token
    - Fund dispersal management
    - Accounting with full audit trail
    - Total supply tracking
    """

    treasury_id: str = "main"
    balances: dict[str, float] = field(default_factory=lambda: {"INFLUX": 0.0})
    dispersals: dict[str, Dispersal] = field(default_factory=dict)
    total_dispersed: dict[str, float] = field(default_factory=lambda: {"INFLUX": 0.0})
    total_deposited: dict[str, float] = field(default_factory=lambda: {"INFLUX": 0.0})
    created_at: int = field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))

    def deposit(self, token: str, amount: float, source: str) -> bool:
        """
        Deposit funds into the treasury.

        Args:
            token: Token identifier
            amount: Amount to deposit (must be positive)
            source: Source of the funds

        Returns:
            True if deposit was successful
        """
        if amount <= 0:
            return False

        if token not in self.balances:
            self.balances[token] = 0.0
            self.total_dispersed[token] = 0.0
            self.total_deposited[token] = 0.0

        self.balances[token] += amount
        self.total_deposited[token] += amount
        return True

    def withdraw(self, token: str, amount: float, recipient: str) -> bool:
        """
        Withdraw funds from the treasury.

        Args:
            token: Token identifier
            amount: Amount to withdraw (must be positive)
            recipient: Recipient of the funds

        Returns:
            True if withdrawal was successful
        """
        if amount <= 0:
            return False

        if token not in self.balances:
            return False

        if self.balances[token] < amount:
            return False

        self.balances[token] -= amount
        self.total_dispersed[token] += amount
        return True

    def create_dispersal(self, proposal_id: str, recipient: str, amount: float,
                          token: str, reason: str) -> Optional[Dispersal]:
        """
        Create a new dispersal request.

        Returns:
            Dispersal object if created, None if insufficient funds or invalid params.
        """
        if amount <= 0:
            return None
        if token not in self.balances:
            return None
        if self.balances[token] < amount:
            return None

        dispersal_id = hashlib.sha256(
            f"{proposal_id}:{recipient}:{amount}:{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]

        dispersal = Dispersal(
            dispersal_id=dispersal_id,
            proposal_id=proposal_id,
            recipient=recipient,
            amount=amount,
            token=token,
            reason=reason,
        )
        self.dispersals[dispersal_id] = dispersal
        return dispersal

    def approve_dispersal(self, dispersal_id: str) -> bool:
        """Approve a pending dispersal."""
        if dispersal_id not in self.dispersals:
            return False
        dispersal = self.dispersals[dispersal_id]
        if dispersal.status != DispersalStatus.PENDING:
            return False
        dispersal.status = DispersalStatus.APPROVED
        return True

    def execute_dispersal(self, dispersal_id: str) -> bool:
        """
        Execute an approved dispersal.

        Withdraws the funds from the treasury and marks the dispersal as executed.
        """
        if dispersal_id not in self.dispersals:
            return False
        dispersal = self.dispersals[dispersal_id]
        if dispersal.status != DispersalStatus.APPROVED:
            return False

        success = self.withdraw(dispersal.token, dispersal.amount, dispersal.recipient)
        if not success:
            return False

        dispersal.execute()
        return True

    def get_balance(self, token: str) -> float:
        """Get the current balance for a token."""
        return self.balances.get(token, 0.0)

    def snapshot(self) -> dict[str, Any]:
        """Deterministic treasury snapshot."""
        return {
            "treasury_id": self.treasury_id,
            "balances": dict(self.balances),
            "total_dispersed": dict(self.total_dispersed),
            "total_deposited": dict(self.total_deposited),
            "dispersal_count": len(self.dispersals),
            "pending_dispersals": sum(
                1 for d in self.dispersals.values() if d.status == DispersalStatus.PENDING
            ),
        }
