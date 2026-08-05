"""
Central coordinator for the InFlux Economic Core.

Orchestrates the economic lifecycle:
    receive events
    ↓
    scheduler
    ↓
    validator
    ↓
    executor
    ↓
    transition
    ↓
    snapshot
    ↓
    metrics

No economic policy, inflation, rewards, or treasury math here.
Only orchestration.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from .economic_context import EconomicContext, create_economic_context
from .economic_state import EconomicState
from .economic_transition import EconomicTransition
from .economic_snapshot import EconomicSnapshot, EconomicSnapshotManager
from .economic_executor import (
    EconomicExecutor,
    EconomicOperation,
    ExecutionReceipt,
)
from .economic_scheduler import EconomicScheduler
from .economic_validator import EconomicValidator, ValidationResult
from .economic_metrics import EconomicMetrics


@dataclass(slots=True)
class BlockResult:
    """
    Result of processing a single block through the economic engine.

    Records:
    - block_height: The block that was processed
    - operation_count: Number of operations executed
    - success_count: Number of successful operations
    - failure_count: Number of failed operations
    - pre_state_root: State root before processing
    - post_state_root: State root after processing
    - snapshot_id: ID of the snapshot taken at this block
    - receipts: Execution receipts for all operations
    """

    block_height: int
    operation_count: int
    success_count: int
    failure_count: int
    pre_state_root: str
    post_state_root: str
    snapshot_id: str
    receipts: list[ExecutionReceipt] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "block_height": self.block_height,
            "operation_count": self.operation_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "pre_state_root": self.pre_state_root,
            "post_state_root": self.post_state_root,
            "snapshot_id": self.snapshot_id,
        }


@dataclass(slots=True)
class EconomicEngine:
    """
    Central coordinator for the InFlux Economic Core.

    Orchestrates the full economic lifecycle:
    1. Receive events from the event bus
    2. Query scheduler for due operations
    3. Validate operations
    4. Execute operations via EconomicExecutor
    5. Record transitions
    6. Create state snapshots
    7. Collect metrics

    Pipeline:
        receive events
        ↓
        scheduler.get_due_operations()
        ↓
        validator.validate()
        ↓
        executor.execute()
        ↓
        transition.record()
        ↓
        snapshot.create()
        ↓
        metrics.record()
    """

    state: EconomicState = field(default_factory=EconomicState)
    context: EconomicContext = field(default_factory=lambda: create_economic_context(block_height=0))
    executor: EconomicExecutor = field(default_factory=EconomicExecutor)
    scheduler: EconomicScheduler = field(default_factory=EconomicScheduler)
    validator: EconomicValidator = field(default_factory=EconomicValidator)
    snapshot_manager: EconomicSnapshotManager = field(default_factory=EconomicSnapshotManager)
    metrics: EconomicMetrics = field(default_factory=EconomicMetrics)
    engine_id: str = field(default_factory=lambda: hashlib.sha256(
        f"economic-engine-{datetime.now(timezone.utc).timestamp()}".encode()
    ).hexdigest()[:16])

    def process_block(
        self,
        block_height: int,
        operations: Optional[list[EconomicOperation]] = None,
        block_timestamp: Optional[int] = None,
    ) -> BlockResult:
        """
        Process a single block through the economic engine.

        Args:
            block_height: The block height to process
            operations: Optional list of operations to execute
            block_timestamp: Block timestamp (defaults to current time)

        Returns:
            BlockResult with execution results
        """
        if block_timestamp is None:
            block_timestamp = int(datetime.now(timezone.utc).timestamp())

        # Update context
        self.context = create_economic_context(
            block_height=block_height,
            block_timestamp=block_timestamp,
            state_root=self.state.state_root,
            epoch=self.state.current_epoch,
            previous_state_root=self.state.state_root,
        )

        pre_state_root = self.state.state_root

        # Get scheduled operations
        scheduled_ops = self.scheduler.get_all_due_operations(block_height)

        # Combine with provided operations
        all_operations = list(scheduled_ops)
        if operations:
            all_operations.extend(operations)

        # Process all operations
        receipts: list[ExecutionReceipt] = []
        success_count = 0
        failure_count = 0

        for operation in all_operations:
            # Validate
            validation = self.validator.validate(operation, self.state, self.context)
            if not validation.valid:
                receipts.append(ExecutionReceipt(
                    operation=operation,
                    transition=None,
                    pre_state_root=pre_state_root,
                    post_state_root=self.state.state_root,
                    success=False,
                    error="; ".join(validation.errors),
                ))
                failure_count += 1
                continue

            # Execute
            receipt = self.executor.execute(operation, self.state, self.context)
            receipts.append(receipt)

            if receipt.success:
                success_count += 1
            else:
                failure_count += 1

            # Record metrics
            self.metrics.record_execution(receipt)

        # Create snapshot
        snapshot = self.snapshot_manager.create_snapshot(
            state=self.state,
            block_height=block_height,
            timestamp=block_timestamp,
        )

        # Record block metrics
        self.metrics.record_block(self.state)

        # Advance epoch if needed
        self.state.blocks_since_epoch_start += 1
        if self.state.blocks_since_epoch_start >= self.state.epoch_length_blocks:
            self.executor.transition.advance_epoch(
                state=self.state,
                block_height=block_height,
            )

        return BlockResult(
            block_height=block_height,
            operation_count=len(all_operations),
            success_count=success_count,
            failure_count=failure_count,
            pre_state_root=pre_state_root,
            post_state_root=self.state.state_root,
            snapshot_id=snapshot.snapshot_id,
            receipts=receipts,
        )

    def execute_operation(
        self,
        operation: EconomicOperation,
    ) -> ExecutionReceipt:
        """
        Execute a single operation directly (bypasses scheduler).

        Args:
            operation: The operation to execute

        Returns:
            ExecutionReceipt
        """
        # Validate
        validation = self.validator.validate(operation, self.state, self.context)
        if not validation.valid:
            return ExecutionReceipt(
                operation=operation,
                transition=None,
                pre_state_root=self.state.state_root,
                post_state_root=self.state.state_root,
                success=False,
                error="; ".join(validation.errors),
            )

        # Execute
        receipt = self.executor.execute(operation, self.state, self.context)

        # Record metrics
        self.metrics.record_execution(receipt)

        return receipt

    def schedule_operation(
        self,
        operation: EconomicOperation,
        target_block_height: int,
        description: str = "",
    ) -> bool:
        """
        Schedule an operation for future execution.

        Args:
            operation: The operation to schedule
            target_block_height: Block at which to execute
            description: Human-readable description

        Returns:
            True if scheduled successfully
        """
        return self.scheduler.schedule(
            operation=operation,
            target_block_height=target_block_height,
            current_block_height=self.context.block_height,
            description=description,
        )

    def get_state(self) -> EconomicState:
        """Get the current economic state."""
        return self.state

    def get_context(self) -> EconomicContext:
        """Get the current execution context."""
        return self.context

    def get_metrics(self) -> EconomicMetrics:
        """Get the current metrics."""
        return self.metrics

    def verify_invariants(self) -> list[str]:
        """Verify economic invariants on the current state."""
        return self.state.verify_invariants()

    def snapshot(self) -> dict[str, Any]:
        """Deterministic engine snapshot."""
        return {
            "engine_id": self.engine_id,
            "state": self.state.snapshot(),
            "context": self.context.snapshot(),
            "executor": self.executor.snapshot(),
            "scheduler": self.scheduler.snapshot(),
            "snapshot_manager": self.snapshot_manager.snapshot(),
            "metrics": self.metrics.snapshot(),
            "invariants": self.verify_invariants(),
        }

    def reset(self) -> None:
        """Reset the engine to initial state."""
        self.state.reset()
        self.context = create_economic_context(block_height=0)
        self.executor.reset()
        self.scheduler.reset()
        self.snapshot_manager.reset()
        self.metrics.reset()
