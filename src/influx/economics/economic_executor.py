"""
THE single mutation path for ALL economic state changes in InFlux.

No module modifies balances directly.
All balance changes flow through EconomicExecutor.execute().

Flow:
    EconomicOperation
    ↓
    validate() (pre-conditions)
    ↓
    execute() (state mutation via EconomicTransition)
    ↓
    snapshot() (state capture)
    ↓
    ExecutionReceipt (audit record)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .economic_context import EconomicContext
from .economic_state import EconomicState
from .economic_transition import EconomicTransition, StateTransition, TransitionType


class OperationType(Enum):
    """Canonical economic operation types."""

    TRANSFER = "transfer"
    MINT = "mint"
    BURN = "burn"
    LOCK = "lock"
    UNLOCK = "unlock"
    RESERVE_UPDATE = "reserve_update"
    EPOCH_ADVANCE = "epoch_advance"
    CONTRACT_PAYOUT = "contract_payout"
    VALIDATOR_REWARD = "validator_reward"
    TREASURY_DISPERSAL = "treasury_dispersal"
    FEE_COLLECTION = "fee_collection"
    EMISSION = "emission"
    GOVERNANCE_EXECUTION = "governance_execution"


@dataclass(slots=True)
class EconomicOperation:
    """
    A single economic operation to be executed.

    This is the atomic unit of economic change.
    Every balance mutation in the protocol is represented
    as an EconomicOperation.
    """

    operation_type: OperationType
    from_account: str
    to_account: str
    amount: float
    token: str = "INFLUX"
    metadata: dict[str, Any] = field(default_factory=dict)
    operation_id: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic operation hash."""
        canonical = {
            "operation_type": self.operation_type.value,
            "from_account": self.from_account,
            "to_account": self.to_account,
            "amount": str(self.amount),
            "token": self.token,
            "metadata": self._canonicalize(self.metadata),
            "operation_id": self.operation_id,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _canonicalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): EconomicOperation._canonicalize(v) for k, v in sorted(value.items())}
        elif isinstance(value, list):
            return [EconomicOperation._canonicalize(v) for v in value]
        elif isinstance(value, float):
            return str(value)
        return value

    @property
    def hash(self) -> str:
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        return {
            "operation_type": self.operation_type.value,
            "from_account": self.from_account,
            "to_account": self.to_account,
            "amount": str(self.amount),
            "token": self.token,
            "metadata": self.metadata,
            "operation_id": self.operation_id,
            "hash": self.hash,
        }


@dataclass(slots=True)
class ExecutionReceipt:
    """
    Receipt for an executed economic operation.

    Records the full audit trail:
    - The original operation
    - The resulting state transition
    - Pre and post state roots
    - Success/failure status
    - Error messages
    """

    operation: EconomicOperation
    transition: Optional[StateTransition]
    pre_state_root: str
    post_state_root: str
    success: bool
    error: str = ""
    execution_time_ns: int = 0

    def snapshot(self) -> dict[str, Any]:
        return {
            "operation": self.operation.snapshot(),
            "transition": self.transition.snapshot() if self.transition else None,
            "pre_state_root": self.pre_state_root,
            "post_state_root": self.post_state_root,
            "success": self.success,
            "error": self.error,
        }


@dataclass(slots=True)
class EconomicExecutor:
    """
    THE single mutation path for ALL economic state changes.

    This is the only component in the entire protocol that
    modifies balances. Every other subsystem must route
    economic changes through this executor.

    Pipeline:
    1. Receive EconomicOperation
    2. Validate pre-conditions
    3. Execute via EconomicTransition
    4. Capture post-state
    5. Return ExecutionReceipt
    """

    transition: EconomicTransition = field(default_factory=EconomicTransition)

    def execute(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        context: EconomicContext,
    ) -> ExecutionReceipt:
        """
        Execute a single economic operation.

        This is THE entry point for all balance mutations.

        Args:
            operation: The operation to execute
            state: The economic state to mutate
            context: The execution context

        Returns:
            ExecutionReceipt with full audit trail
        """
        pre_state_root = state.state_root
        result_transition: Optional[StateTransition] = None
        success = False
        error = ""

        try:
            if operation.operation_type == OperationType.TRANSFER:
                result_transition = self.transition.apply_transfer(
                    state=state,
                    from_account=operation.from_account,
                    to_account=operation.to_account,
                    amount=operation.amount,
                    token=operation.token,
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = result_transition is not None
                if not success:
                    error = "Transfer failed: insufficient funds or invalid params"

            elif operation.operation_type == OperationType.MINT:
                result_transition = self.transition.apply_mint(
                    state=state,
                    to_account=operation.to_account,
                    amount=operation.amount,
                    token=operation.token,
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = result_transition is not None
                if not success:
                    error = "Mint failed: exceeds max supply or invalid params"

            elif operation.operation_type == OperationType.BURN:
                result_transition = self.transition.apply_burn(
                    state=state,
                    from_account=operation.from_account,
                    amount=operation.amount,
                    token=operation.token,
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = result_transition is not None
                if not success:
                    error = "Burn failed: insufficient funds or invalid params"

            elif operation.operation_type == OperationType.LOCK:
                result_transition = self.transition.apply_lock(
                    state=state,
                    account=operation.from_account,
                    amount=operation.amount,
                    token=operation.token,
                    lock_until_block=operation.metadata.get("lock_until_block", 0),
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = result_transition is not None
                if not success:
                    error = "Lock failed: insufficient funds or invalid params"

            elif operation.operation_type == OperationType.UNLOCK:
                result_transition = self.transition.apply_unlock(
                    state=state,
                    account=operation.from_account,
                    amount=operation.amount,
                    token=operation.token,
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = result_transition is not None
                if not success:
                    error = "Unlock failed: insufficient locked balance or invalid params"

            elif operation.operation_type == OperationType.RESERVE_UPDATE:
                result_transition = self.transition.apply_reserve_update(
                    state=state,
                    new_reserve_size=operation.amount,
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = True

            elif operation.operation_type == OperationType.EPOCH_ADVANCE:
                result_transition = self.transition.advance_epoch(
                    state=state,
                    block_height=context.block_height,
                    metadata=operation.metadata,
                )
                success = True

            else:
                error = f"Unknown operation type: {operation.operation_type}"
                success = False

        except Exception as e:
            error = f"Execution error: {e}"
            success = False

        return ExecutionReceipt(
            operation=operation,
            transition=result_transition,
            pre_state_root=pre_state_root,
            post_state_root=state.state_root,
            success=success,
            error=error,
        )

    def execute_batch(
        self,
        operations: list[EconomicOperation],
        state: EconomicState,
        context: EconomicContext,
    ) -> list[ExecutionReceipt]:
        """
        Execute a batch of operations atomically.

        Each operation is executed in order.
        If any operation fails, subsequent operations still execute
        (failures are isolated per operation).

        Args:
            operations: Ordered list of operations
            state: The economic state to mutate
            context: The execution context

        Returns:
            List of ExecutionReceipts in corresponding order
        """
        return [self.execute(op, state, context) for op in operations]

    def get_execution_count(self) -> int:
        """Get total number of executed transitions."""
        return self.transition.get_transition_count()

    def verify_execution_chain(self) -> bool:
        """Verify integrity of the execution chain."""
        return self.transition.verify_chain()

    def snapshot(self) -> dict[str, Any]:
        return {
            "execution_count": self.get_execution_count(),
            "chain_valid": self.verify_execution_chain(),
            "transitions": self.transition.snapshot(),
        }

    def reset(self) -> None:
        """Reset the executor state."""
        self.transition.reset()
