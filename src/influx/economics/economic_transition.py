"""
Deterministic state transition engine for the InFlux Economic Core.

Applies state diffs deterministically to the EconomicState.
Each transition is validated, hashed, and recorded for replay.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .economic_state import EconomicState


class TransitionType(Enum):
    """Canonical state transition types."""

    TRANSFER = "transfer"
    MINT = "mint"
    BURN = "burn"
    LOCK = "lock"
    UNLOCK = "unlock"
    RESERVE_UPDATE = "reserve_update"
    SUPPLY_UPDATE = "supply_update"
    EPOCH_ADVANCE = "epoch_advance"
    ACCOUNT_CREATE = "account_create"
    ACCOUNT_UPDATE = "account_update"
    EMISSION_SCHEDULE = "emission_schedule"
    PAYOUT_SCHEDULE = "payout_schedule"
    RELEASE_SCHEDULE = "release_schedule"
    EMISSION_EXECUTE = "emission_execute"
    PAYOUT_EXECUTE = "payout_execute"
    RELEASE_EXECUTE = "release_execute"


@dataclass(slots=True)
class StateTransition:
    """
    A single deterministic state transition.

    Records:
    - transition_type: What kind of transition
    - account: Affected account (if applicable)
    - token: Token identifier
    - delta: The change amount (positive or negative)
    - metadata: Additional transition data
    - block_height: Block at which this occurred
    - sequence: Order within the block
    - previous_hash: Hash of previous transition
    """

    transition_type: TransitionType
    account: str
    token: str = "INFLUX"
    delta: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    block_height: int = 0
    sequence: int = 0
    previous_hash: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic transition hash."""
        canonical = {
            "transition_type": self.transition_type.value,
            "account": self.account,
            "token": self.token,
            "delta": str(self.delta),
            "metadata": self._canonicalize(self.metadata),
            "block_height": self.block_height,
            "sequence": self.sequence,
            "previous_hash": self.previous_hash,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _canonicalize(value: Any) -> Any:
        """Recursively canonicalize for deterministic serialization."""
        if isinstance(value, dict):
            return {str(k): StateTransition._canonicalize(v) for k, v in sorted(value.items())}
        elif isinstance(value, list):
            return [StateTransition._canonicalize(v) for v in value]
        elif isinstance(value, float):
            return str(value)
        return value

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        """Deterministic transition snapshot."""
        return {
            "transition_type": self.transition_type.value,
            "account": self.account,
            "token": self.token,
            "delta": str(self.delta),
            "metadata": self.metadata,
            "block_height": self.block_height,
            "sequence": self.sequence,
            "hash": self.hash,
        }


@dataclass(slots=True)
class EconomicTransition:
    """
    Deterministic state transition engine.

    Applies validated transitions to the EconomicState.
    Each transition is recorded for replay and audit.

    The engine enforces:
    - No negative balances after transfer/burn
    - Supply conservation (mint/burn tracked)
    - Valid account existence
    - Deterministic ordering
    """

    _transitions: list[StateTransition] = field(default_factory=list)
    _sequence_counter: int = 0

    def apply_transfer(
        self,
        state: EconomicState,
        from_account: str,
        to_account: str,
        amount: float,
        token: str = "INFLUX",
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[StateTransition]:
        """
        Apply a token transfer between accounts.

        Args:
            state: The economic state to mutate
            from_account: Source account address
            to_account: Destination account address
            amount: Amount to transfer (must be positive)
            token: Token identifier
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition if successful, None if validation fails
        """
        if amount <= 0:
            return None

        from_acct = state.get_account(from_account)
        if from_acct.balances.get(token, 0.0) < amount:
            return None

        to_acct = state.get_account(to_account)

        # Apply balances
        from_acct.balances[token] = from_acct.balances.get(token, 0.0) - amount
        to_acct.balances[token] = to_acct.balances.get(token, 0.0) + amount

        transition = self._record_transition(
            transition_type=TransitionType.TRANSFER,
            account=from_account,
            token=token,
            delta=-amount,
            block_height=block_height,
            metadata={
                "from": from_account,
                "to": to_account,
                "amount": str(amount),
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def apply_mint(
        self,
        state: EconomicState,
        to_account: str,
        amount: float,
        token: str = "INFLUX",
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[StateTransition]:
        """
        Mint new tokens to an account.

        Args:
            state: The economic state to mutate
            to_account: Destination account address
            amount: Amount to mint (must be positive)
            token: Token identifier
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition if successful, None if validation fails
        """
        if amount <= 0:
            return None

        # Check max supply cap
        if state.supply.max_supply > 0:
            if state.supply.total_supply + amount > state.supply.max_supply:
                return None

        acct = state.get_account(to_account)
        acct.balances[token] = acct.balances.get(token, 0.0) + amount

        # Update supply
        state.supply.total_supply += amount
        state.supply.circulating_supply += amount

        transition = self._record_transition(
            transition_type=TransitionType.MINT,
            account=to_account,
            token=token,
            delta=amount,
            block_height=block_height,
            metadata={
                "to": to_account,
                "amount": str(amount),
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def apply_burn(
        self,
        state: EconomicState,
        from_account: str,
        amount: float,
        token: str = "INFLUX",
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[StateTransition]:
        """
        Burn tokens from an account.

        Args:
            state: The economic state to mutate
            from_account: Source account address
            amount: Amount to burn (must be positive)
            token: Token identifier
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition if successful, None if validation fails
        """
        if amount <= 0:
            return None

        acct = state.get_account(from_account)
        if acct.balances.get(token, 0.0) < amount:
            return None

        acct.balances[token] = acct.balances.get(token, 0.0) - amount

        # Update supply
        state.supply.total_supply -= amount
        state.supply.circulating_supply -= amount
        state.supply.burned_supply += amount

        transition = self._record_transition(
            transition_type=TransitionType.BURN,
            account=from_account,
            token=token,
            delta=-amount,
            block_height=block_height,
            metadata={
                "from": from_account,
                "amount": str(amount),
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def apply_lock(
        self,
        state: EconomicState,
        account: str,
        amount: float,
        token: str = "INFLUX",
        lock_until_block: int = 0,
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[StateTransition]:
        """
        Lock tokens in an account (e.g., for staking or vesting).

        Args:
            state: The economic state to mutate
            account: Account address
            amount: Amount to lock (must be positive)
            token: Token identifier
            lock_until_block: Block height until which tokens are locked
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition if successful, None if validation fails
        """
        if amount <= 0:
            return None

        acct = state.get_account(account)
        if acct.balances.get(token, 0.0) < amount:
            return None

        acct.balances[token] = acct.balances.get(token, 0.0) - amount
        acct.locked_balances[token] = acct.locked_balances.get(token, 0.0) + amount

        # Update supply tracking
        state.supply.circulating_supply -= amount
        state.supply.locked_supply += amount

        transition = self._record_transition(
            transition_type=TransitionType.LOCK,
            account=account,
            token=token,
            delta=-amount,
            block_height=block_height,
            metadata={
                "account": account,
                "amount": str(amount),
                "lock_until_block": lock_until_block,
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def apply_unlock(
        self,
        state: EconomicState,
        account: str,
        amount: float,
        token: str = "INFLUX",
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[StateTransition]:
        """
        Unlock tokens in an account.

        Args:
            state: The economic state to mutate
            account: Account address
            amount: Amount to unlock (must be positive)
            token: Token identifier
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition if successful, None if validation fails
        """
        if amount <= 0:
            return None

        acct = state.get_account(account)
        if acct.locked_balances.get(token, 0.0) < amount:
            return None

        acct.locked_balances[token] = acct.locked_balances.get(token, 0.0) - amount
        acct.balances[token] = acct.balances.get(token, 0.0) + amount

        # Update supply tracking
        state.supply.circulating_supply += amount
        state.supply.locked_supply -= amount

        transition = self._record_transition(
            transition_type=TransitionType.UNLOCK,
            account=account,
            token=token,
            delta=amount,
            block_height=block_height,
            metadata={
                "account": account,
                "amount": str(amount),
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def apply_reserve_update(
        self,
        state: EconomicState,
        new_reserve_size: float,
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StateTransition:
        """
        Update the reserve size and recalculate ratio.

        Args:
            state: The economic state to mutate
            new_reserve_size: New reserve balance
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition
        """
        state.reserve.reserve_size = new_reserve_size
        if state.supply.total_supply > 0:
            state.reserve.current_ratio = new_reserve_size / state.supply.total_supply
        else:
            state.reserve.current_ratio = 0.0
        state.reserve.last_rebalance_height = block_height

        transition = self._record_transition(
            transition_type=TransitionType.RESERVE_UPDATE,
            account="reserve",
            token="INFLUX",
            delta=new_reserve_size - state.reserve.reserve_size,
            block_height=block_height,
            metadata={
                "new_reserve_size": str(new_reserve_size),
                "new_ratio": str(state.reserve.current_ratio),
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def advance_epoch(
        self,
        state: EconomicState,
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StateTransition:
        """
        Advance to the next epoch.

        Args:
            state: The economic state to mutate
            block_height: Current block height
            metadata: Optional transition metadata

        Returns:
            StateTransition
        """
        state.current_epoch += 1
        state.blocks_since_epoch_start = 0

        transition = self._record_transition(
            transition_type=TransitionType.EPOCH_ADVANCE,
            account="system",
            block_height=block_height,
            metadata={
                "new_epoch": state.current_epoch,
                **(metadata or {}),
            },
        )

        state.update_state_root()
        return transition

    def _record_transition(
        self,
        transition_type: TransitionType,
        account: str,
        token: str = "INFLUX",
        delta: float = 0.0,
        block_height: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StateTransition:
        """Record a transition with chain integrity."""
        previous_hash = self._transitions[-1].hash if self._transitions else ""

        transition = StateTransition(
            transition_type=transition_type,
            account=account,
            token=token,
            delta=delta,
            metadata=metadata or {},
            block_height=block_height,
            sequence=self._sequence_counter,
            previous_hash=previous_hash,
        )

        self._transitions.append(transition)
        self._sequence_counter += 1
        return transition

    def get_transitions(
        self,
        start: int = 0,
        end: Optional[int] = None,
    ) -> list[StateTransition]:
        """Get recorded transitions in range."""
        if end is None:
            end = len(self._transitions)
        return list(self._transitions[start:end])

    def get_transition_count(self) -> int:
        """Get total number of recorded transitions."""
        return len(self._transitions)

    def verify_chain(self) -> bool:
        """Verify integrity of the transition chain."""
        for i, t in enumerate(self._transitions):
            if not t.hash == t.compute_hash():
                return False
            if i > 0 and t.previous_hash != self._transitions[i - 1].hash:
                return False
        return True

    def snapshot(self) -> dict[str, Any]:
        """Deterministic transition engine snapshot."""
        return {
            "transition_count": self.get_transition_count(),
            "sequence_counter": self._sequence_counter,
            "chain_valid": self.verify_chain(),
            "transitions": [t.snapshot() for t in self._transitions],
        }

    def reset(self) -> None:
        """Reset the transition engine."""
        self._transitions.clear()
        self._sequence_counter = 0
