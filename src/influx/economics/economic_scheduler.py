"""
Deterministic economic event scheduler for the InFlux protocol.

Answers one question: "What economic operations are due at this block?"

The scheduler only schedules. It does NOT execute operations.
Execution is handled by EconomicExecutor.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional

from .economic_context import EconomicContext
from .economic_executor import EconomicOperation, OperationType
from .economic_state import EconomicState


@dataclass(slots=True)
class ScheduledOperation:
    """
    A scheduled economic operation.

    Records when an operation should be executed and
    the conditions for execution.
    """

    operation: EconomicOperation
    target_block_height: int
    scheduled_at_block: int
    description: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic hash."""
        canonical = {
            "operation": self.operation.snapshot(),
            "target_block_height": self.target_block_height,
            "scheduled_at_block": self.scheduled_at_block,
            "description": self.description,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        return {
            "operation": self.operation.snapshot(),
            "target_block_height": self.target_block_height,
            "scheduled_at_block": self.scheduled_at_block,
            "description": self.description,
            "hash": self.hash,
        }


@dataclass(slots=True)
class EconomicScheduler:
    """
    Deterministic economic event scheduler.

    Only answers: "What economic operations are due at this block?"

    The scheduler:
    - Stores scheduled operations by target block
    - Returns due operations for a given block
    - Tracks completed operations
    - Never executes operations directly
    """

    _scheduled: dict[int, list[ScheduledOperation]] = field(default_factory=dict)
    _completed: set[str] = field(default_factory=set)
    _schedule_count: int = 0

    def schedule(
        self,
        operation: EconomicOperation,
        target_block_height: int,
        current_block_height: int,
        description: str = "",
    ) -> bool:
        """
        Schedule an operation for future execution.

        Args:
            operation: The operation to schedule
            target_block_height: The block at which to execute
            current_block_height: The current block height (for validation)
            description: Human-readable description

        Returns:
            True if scheduled successfully
        """
        if target_block_height <= current_block_height:
            return False

        if operation.amount <= 0:
            return False

        scheduled = ScheduledOperation(
            operation=operation,
            target_block_height=target_block_height,
            scheduled_at_block=current_block_height,
            description=description or f"{operation.operation_type.value} operation",
        )

        if target_block_height not in self._scheduled:
            self._scheduled[target_block_height] = []

        self._scheduled[target_block_height].append(scheduled)
        self._schedule_count += 1
        return True

    def get_due_operations(
        self,
        block_height: int,
    ) -> list[EconomicOperation]:
        """
        Get all operations due at the given block height.

        Args:
            block_height: The current block height

        Returns:
            List of operations scheduled for this block
        """
        due = self._scheduled.get(block_height, [])
        operations = []

        for scheduled in due:
            op_hash = scheduled.operation.hash
            if op_hash not in self._completed:
                operations.append(scheduled.operation)
                self._completed.add(op_hash)

        return operations

    def get_all_due_operations(
        self,
        block_height: int,
    ) -> list[EconomicOperation]:
        """
        Get all operations due at or before the given block height.

        Args:
            block_height: The current block height

        Returns:
            List of operations scheduled for this block or earlier
        """
        operations = []
        for height in sorted(self._scheduled.keys()):
            if height > block_height:
                break
            operations.extend(self.get_due_operations(height))
        return operations

    def has_pending_at(self, block_height: int) -> bool:
        """Check if there are pending operations at a given block."""
        return block_height in self._scheduled

    def get_pending_count(self) -> int:
        """Get total number of pending scheduled operations."""
        total = 0
        for height, ops in self._scheduled.items():
            for op in ops:
                if op.operation.hash not in self._completed:
                    total += 1
        return total

    def get_scheduled_blocks(self) -> list[int]:
        """Get all block heights with scheduled operations."""
        return sorted(self._scheduled.keys())

    def get_schedule_count(self) -> int:
        """Get total number of schedules made."""
        return self._schedule_count

    def snapshot(self) -> dict[str, Any]:
        """Deterministic scheduler snapshot."""
        return {
            "schedule_count": self._schedule_count,
            "pending_count": self.get_pending_count(),
            "completed_count": len(self._completed),
            "scheduled_blocks": self.get_scheduled_blocks(),
            "scheduled": {
                str(height): [s.snapshot() for s in ops]
                for height, ops in sorted(self._scheduled.items())
            },
        }

    def reset(self) -> None:
        """Reset the scheduler."""
        self._scheduled.clear()
        self._completed.clear()
        self._schedule_count = 0
