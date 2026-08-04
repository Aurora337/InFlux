"""
Deterministic economic operation validator for the InFlux protocol.

Validates operations BEFORE execution (pre-conditions).
The validator never mutates state — it only checks conditions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .economic_context import EconomicContext
from .economic_executor import EconomicOperation, OperationType
from .economic_state import EconomicState


@dataclass(slots=True)
class ValidationResult:
    """
    Result of an economic operation validation.

    Records:
    - valid: Whether the operation passed all checks
    - errors: List of validation error messages
    - warnings: List of non-fatal warnings
    """

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


@dataclass(slots=True)
class EconomicValidator:
    """
    Validates economic operations BEFORE execution.

    The validator checks pre-conditions such as:
    - Sufficient balance for transfers/burns
    - Valid account addresses
    - Positive amounts
    - Max supply caps
    - Reserve ratio bounds
    - Epoch transition validity

    The validator NEVER mutates state.
    """

    def validate(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        context: EconomicContext,
    ) -> ValidationResult:
        """
        Validate an economic operation before execution.

        Args:
            operation: The operation to validate
            state: The current economic state
            context: The execution context

        Returns:
            ValidationResult with any errors or warnings
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Common validations for all operations
        self._validate_common(operation, state, errors, warnings)

        # Type-specific validations
        if operation.operation_type == OperationType.TRANSFER:
            self._validate_transfer(operation, state, errors, warnings)
        elif operation.operation_type == OperationType.MINT:
            self._validate_mint(operation, state, errors, warnings)
        elif operation.operation_type == OperationType.BURN:
            self._validate_burn(operation, state, errors, warnings)
        elif operation.operation_type == OperationType.LOCK:
            self._validate_lock(operation, state, errors, warnings)
        elif operation.operation_type == OperationType.UNLOCK:
            self._validate_unlock(operation, state, errors, warnings)
        elif operation.operation_type == OperationType.RESERVE_UPDATE:
            self._validate_reserve_update(operation, state, errors, warnings)
        elif operation.operation_type == OperationType.EPOCH_ADVANCE:
            self._validate_epoch_advance(operation, state, context, errors, warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _validate_common(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate common pre-conditions for all operations."""
        if operation.amount <= 0:
            errors.append("Amount must be positive")

        if not operation.from_account and operation.operation_type not in [
            OperationType.MINT,
            OperationType.EPOCH_ADVANCE,
        ]:
            errors.append("From account is required")

        if not operation.to_account and operation.operation_type in [
            OperationType.TRANSFER,
            OperationType.MINT,
        ]:
            errors.append("To account is required")

    def _validate_transfer(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate a transfer operation."""
        balance = state.get_balance(operation.from_account, operation.token)
        if balance < operation.amount:
            errors.append(
                f"Insufficient balance: {balance} < {operation.amount} for {operation.token}"
            )

    def _validate_mint(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate a mint operation."""
        if state.supply.max_supply > 0:
            if state.supply.total_supply + operation.amount > state.supply.max_supply:
                errors.append(
                    f"Mint would exceed max supply: "
                    f"{state.supply.total_supply + operation.amount} > {state.supply.max_supply}"
                )

    def _validate_burn(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate a burn operation."""
        balance = state.get_balance(operation.from_account, operation.token)
        if balance < operation.amount:
            errors.append(
                f"Insufficient balance for burn: {balance} < {operation.amount}"
            )

    def _validate_lock(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate a lock operation."""
        balance = state.get_balance(operation.from_account, operation.token)
        if balance < operation.amount:
            errors.append(
                f"Insufficient balance for lock: {balance} < {operation.amount}"
            )

    def _validate_unlock(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate an unlock operation."""
        if operation.from_account not in state.accounts:
            errors.append(f"Account not found: {operation.from_account}")
            return

        locked = state.accounts[operation.from_account].locked_balances.get(
            operation.token, 0.0
        )
        if locked < operation.amount:
            errors.append(
                f"Insufficient locked balance for unlock: {locked} < {operation.amount}"
            )

    def _validate_reserve_update(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate a reserve update operation."""
        if operation.amount < 0:
            errors.append("Reserve size cannot be negative")

        if state.supply.total_supply > 0:
            new_ratio = operation.amount / state.supply.total_supply
            if new_ratio > 1.0:
                warnings.append(
                    f"Reserve ratio would exceed 1.0: {new_ratio}"
                )

    def _validate_epoch_advance(
        self,
        operation: EconomicOperation,
        state: EconomicState,
        context: EconomicContext,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate an epoch advance operation."""
        if state.blocks_since_epoch_start < state.epoch_length_blocks:
            warnings.append(
                f"Epoch not yet complete: "
                f"{state.blocks_since_epoch_start} < {state.epoch_length_blocks}"
            )

    def validate_batch(
        self,
        operations: list[EconomicOperation],
        state: EconomicState,
        context: EconomicContext,
    ) -> list[ValidationResult]:
        """
        Validate a batch of operations.

        Args:
            operations: Ordered list of operations
            state: The current economic state
            context: The execution context

        Returns:
            List of ValidationResults in corresponding order
        """
        return [self.validate(op, state, context) for op in operations]

    def snapshot(self) -> dict[str, Any]:
        """Deterministic validator snapshot."""
        return {
            "validator_type": "EconomicValidator",
            "version": "1.0.0",
        }
