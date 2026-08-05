"""
Deterministic economic state for the InFlux protocol.

THE single source of truth for all economic state.
No module modifies balances directly.
All balance changes flow through EconomicExecutor.execute().

Properties:
- Current Supply (total, circulating, locked)
- Reserve (size, ratio)
- Treasury (balances, pending dispersals)
- Locked Assets (vesting, staking)
- Validator Rewards (pending, distributed)
- Pending Releases (scheduled unlocks)
- Emission Queue (scheduled issuances)
- Scheduled Payouts (governance-approved)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class EconomicAccount:
    """
    A single economic account in the system.

    Accounts are identified by a unique address string
    and carry token balances and metadata.
    """

    address: str
    balances: dict[str, float] = field(default_factory=lambda: {"INFLUX": 0.0})
    locked_balances: dict[str, float] = field(default_factory=dict)
    account_type: str = "user"  # user, validator, treasury, contract, reserve
    nonce: int = 0

    def snapshot(self) -> dict[str, Any]:
        """Deterministic account snapshot."""
        return {
            "address": self.address,
            "balances": dict(self.balances),
            "locked_balances": dict(self.locked_balances),
            "account_type": self.account_type,
            "nonce": self.nonce,
        }


@dataclass(slots=True)
class SupplyInfo:
    """
    Deterministic supply information.

    Tracks:
    - total_supply: Total tokens ever minted
    - circulating_supply: Tokens in circulation (not locked/burned)
    - locked_supply: Tokens in vesting, staking, or governance locks
    - burned_supply: Tokens permanently removed from circulation
    - max_supply: Maximum supply cap (0 = no cap)
    """

    total_supply: float = 0.0
    circulating_supply: float = 0.0
    locked_supply: float = 0.0
    burned_supply: float = 0.0
    max_supply: float = 0.0

    def snapshot(self) -> dict[str, Any]:
        """Deterministic supply snapshot."""
        return {
            "total_supply": str(self.total_supply),
            "circulating_supply": str(self.circulating_supply),
            "locked_supply": str(self.locked_supply),
            "burned_supply": str(self.burned_supply),
            "max_supply": str(self.max_supply),
        }


@dataclass(slots=True)
class ReserveInfo:
    """
    Deterministic reserve information.

    Tracks:
    - reserve_size: Current reserve balance
    - target_ratio: Target reserve ratio (e.g., 0.5 = 50%)
    - current_ratio: Current actual reserve ratio
    - last_rebalance_height: Block height of last rebalance
    """

    reserve_size: float = 0.0
    target_ratio: float = 0.5
    current_ratio: float = 0.0
    last_rebalance_height: int = 0

    def snapshot(self) -> dict[str, Any]:
        """Deterministic reserve snapshot."""
        return {
            "reserve_size": str(self.reserve_size),
            "target_ratio": str(self.target_ratio),
            "current_ratio": str(self.current_ratio),
            "last_rebalance_height": self.last_rebalance_height,
        }


@dataclass(slots=True)
class EconomicState:
    """
    THE deterministic economic state for the InFlux protocol.

    This is the single source of truth for all economic data.
    No other module should hold authoritative economic state.

    State categories:
    - Supply tracking (total, circulating, locked, burned)
    - Reserve information (size, ratio, target)
    - Account balances (all addresses)
    - Pending operations (scheduled for future blocks)
    - Epoch data (current epoch, rewards, emissions)
    """

    # Supply
    supply: SupplyInfo = field(default_factory=SupplyInfo)

    # Reserve
    reserve: ReserveInfo = field(default_factory=ReserveInfo)

    # Accounts
    accounts: dict[str, EconomicAccount] = field(default_factory=dict)

    # Epoch tracking
    current_epoch: int = 0
    blocks_since_epoch_start: int = 0
    epoch_length_blocks: int = 10000

    # Pending operations (scheduled for future execution)
    pending_emissions: list[dict[str, Any]] = field(default_factory=list)
    pending_payouts: list[dict[str, Any]] = field(default_factory=list)
    pending_releases: list[dict[str, Any]] = field(default_factory=list)

    # State root for verification
    state_root: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def get_account(self, address: str) -> EconomicAccount:
        """
        Get or create an account by address.

        Args:
            address: The account address

        Returns:
            The EconomicAccount (created if not exists)
        """
        if address not in self.accounts:
            self.accounts[address] = EconomicAccount(address=address)
        return self.accounts[address]

    def has_account(self, address: str) -> bool:
        """Check if an account exists."""
        return address in self.accounts

    def get_balance(self, address: str, token: str = "INFLUX") -> float:
        """
        Get the balance of an account for a specific token.

        Args:
            address: The account address
            token: The token identifier

        Returns:
            The balance (0.0 if account or token doesn't exist)
        """
        if address not in self.accounts:
            return 0.0
        return self.accounts[address].balances.get(token, 0.0)

    def compute_state_root(self) -> str:
        """Compute deterministic state root hash."""
        canonical = {
            "supply": self.supply.snapshot(),
            "reserve": self.reserve.snapshot(),
            "accounts": {
                addr: acct.snapshot()
                for addr, acct in sorted(self.accounts.items())
            },
            "current_epoch": self.current_epoch,
            "pending_emissions": self.pending_emissions,
            "pending_payouts": self.pending_payouts,
            "pending_releases": self.pending_releases,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def compute_hash(self) -> str:
        """Compute deterministic state hash."""
        return self.compute_state_root()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def update_state_root(self) -> None:
        """Update the state root and cache."""
        self.state_root = self.compute_state_root()
        self._hash = self.state_root

    def snapshot(self) -> dict[str, Any]:
        """Deterministic economic state snapshot."""
        return {
            "supply": self.supply.snapshot(),
            "reserve": self.reserve.snapshot(),
            "account_count": len(self.accounts),
            "accounts": {
                addr: acct.snapshot()
                for addr, acct in sorted(self.accounts.items())
            },
            "current_epoch": self.current_epoch,
            "blocks_since_epoch_start": self.blocks_since_epoch_start,
            "pending_emissions_count": len(self.pending_emissions),
            "pending_payouts_count": len(self.pending_payouts),
            "pending_releases_count": len(self.pending_releases),
            "state_root": self.state_root,
            "hash": self.hash,
        }

    def clone(self) -> EconomicState:
        """
        Create a deep clone of this state.

        Useful for simulating state transitions without side effects.
        """
        state = EconomicState(
            supply=SupplyInfo(
                total_supply=self.supply.total_supply,
                circulating_supply=self.supply.circulating_supply,
                locked_supply=self.supply.locked_supply,
                burned_supply=self.supply.burned_supply,
                max_supply=self.supply.max_supply,
            ),
            reserve=ReserveInfo(
                reserve_size=self.reserve.reserve_size,
                target_ratio=self.reserve.target_ratio,
                current_ratio=self.reserve.current_ratio,
                last_rebalance_height=self.reserve.last_rebalance_height,
            ),
            current_epoch=self.current_epoch,
            blocks_since_epoch_start=self.blocks_since_epoch_start,
            epoch_length_blocks=self.epoch_length_blocks,
        )

        # Deep copy accounts
        for addr, acct in self.accounts.items():
            state.accounts[addr] = EconomicAccount(
                address=acct.address,
                balances=dict(acct.balances),
                locked_balances=dict(acct.locked_balances),
                account_type=acct.account_type,
                nonce=acct.nonce,
            )

        # Deep copy pending operations
        state.pending_emissions = list(self.pending_emissions)
        state.pending_payouts = list(self.pending_payouts)
        state.pending_releases = list(self.pending_releases)

        return state

    def verify_invariants(self) -> list[str]:
        """
        Verify basic economic invariants.

        Returns:
            List of violated invariant descriptions (empty if all pass)
        """
        violations: list[str] = []

        # Supply never negative
        if self.supply.total_supply < 0:
            violations.append("Total supply is negative")
        if self.supply.circulating_supply < 0:
            violations.append("Circulating supply is negative")
        if self.supply.locked_supply < 0:
            violations.append("Locked supply is negative")
        if self.supply.burned_supply < 0:
            violations.append("Burned supply is negative")

        # Supply conservation: total >= circulating + locked
        if self.supply.total_supply < self.supply.circulating_supply + self.supply.locked_supply:
            violations.append(
                "Total supply less than circulating + locked"
            )

        # Reserve ratio bounds
        if self.reserve.current_ratio < 0 or self.reserve.current_ratio > 1:
            violations.append("Reserve ratio out of [0, 1] bounds")

        # Max supply cap
        if self.supply.max_supply > 0 and self.supply.total_supply > self.supply.max_supply:
            violations.append("Total supply exceeds max supply cap")

        return violations

    def reset(self) -> None:
        """Reset state to empty."""
        self.supply = SupplyInfo()
        self.reserve = ReserveInfo()
        self.accounts.clear()
        self.current_epoch = 0
        self.blocks_since_epoch_start = 0
        self.pending_emissions.clear()
        self.pending_payouts.clear()
        self.pending_releases.clear()
        self.state_root = ""
        self._hash = None
