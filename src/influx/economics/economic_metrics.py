"""
Deterministic economic metrics for the InFlux protocol.

Metrics observe and report. They NEVER influence execution.
All metrics are derived from the EconomicState and execution receipts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .economic_context import EconomicContext
from .economic_executor import ExecutionReceipt, OperationType
from .economic_state import EconomicState


@dataclass(slots=True)
class EconomicMetrics:
    """
    Deterministic economic metrics collector.

    Metrics observe the economic state and execution receipts.
    They NEVER influence execution or mutate state.

    Collected metrics:
    - TPS (transactions per second)
    - Economic throughput
    - Operation counts by type
    - Supply metrics
    - Reserve metrics
    - Fee volume
    - Treasury utilization
    """

    # Operation counts
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    operations_by_type: dict[str, int] = field(default_factory=dict)

    # Supply metrics
    last_total_supply: float = 0.0
    last_circulating_supply: float = 0.0
    last_locked_supply: float = 0.0
    last_burned_supply: float = 0.0

    # Reserve metrics
    last_reserve_size: float = 0.0
    last_reserve_ratio: float = 0.0

    # Throughput
    operations_per_block: int = 0
    total_blocks_tracked: int = 0

    def record_execution(self, receipt: ExecutionReceipt) -> None:
        """
        Record metrics from an execution receipt.

        Args:
            receipt: The execution receipt to record
        """
        self.total_operations += 1

        if receipt.success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1

        op_type = receipt.operation.operation_type.value
        self.operations_by_type[op_type] = self.operations_by_type.get(op_type, 0) + 1

    def record_block(self, state: EconomicState) -> None:
        """
        Record metrics at block boundaries.

        Args:
            state: The economic state at the block boundary
        """
        self.last_total_supply = state.supply.total_supply
        self.last_circulating_supply = state.supply.circulating_supply
        self.last_locked_supply = state.supply.locked_supply
        self.last_burned_supply = state.supply.burned_supply
        self.last_reserve_size = state.reserve.reserve_size
        self.last_reserve_ratio = state.reserve.current_ratio
        self.total_blocks_tracked += 1

    def get_success_rate(self) -> float:
        """Get the success rate of operations."""
        if self.total_operations == 0:
            return 1.0
        return self.successful_operations / self.total_operations

    def get_operation_count_by_type(self, operation_type: OperationType) -> int:
        """Get the count of operations for a specific type."""
        return self.operations_by_type.get(operation_type.value, 0)

    def snapshot(self) -> dict[str, Any]:
        """Deterministic metrics snapshot."""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": str(self.get_success_rate()),
            "operations_by_type": dict(self.operations_by_type),
            "supply": {
                "total": str(self.last_total_supply),
                "circulating": str(self.last_circulating_supply),
                "locked": str(self.last_locked_supply),
                "burned": str(self.last_burned_supply),
            },
            "reserve": {
                "size": str(self.last_reserve_size),
                "ratio": str(self.last_reserve_ratio),
            },
            "blocks_tracked": self.total_blocks_tracked,
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.operations_by_type.clear()
        self.last_total_supply = 0.0
        self.last_circulating_supply = 0.0
        self.last_locked_supply = 0.0
        self.last_burned_supply = 0.0
        self.last_reserve_size = 0.0
        self.last_reserve_ratio = 0.0
        self.operations_per_block = 0
        self.total_blocks_tracked = 0
