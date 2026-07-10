from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionMetrics:
    """
    Tracks deterministic execution activity.
    """

    transactions_executed: int = 0

    successful_executions: int = 0

    failed_executions: int = 0

    blocks_executed: int = 0

    total_gas_used: int = 0

    average_execution_time: float = 0.0

    def record_success(
        self,
        gas_used: int = 0,
    ) -> None:

        self.transactions_executed += 1

        self.successful_executions += 1

        self.total_gas_used += gas_used

    def record_failure(
        self,
    ) -> None:

        self.transactions_executed += 1

        self.failed_executions += 1

    def record_block(
        self,
    ) -> None:

        self.blocks_executed += 1

    def update_execution_time(
        self,
        seconds: float,
    ) -> None:
        """
        Rolling deterministic average.
        """

        if self.average_execution_time == 0.0:
            self.average_execution_time = seconds
            return

        self.average_execution_time = (
            self.average_execution_time + seconds
        ) / 2.0

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "transactions_executed":
                self.transactions_executed,

            "successful_executions":
                self.successful_executions,

            "failed_executions":
                self.failed_executions,

            "blocks_executed":
                self.blocks_executed,

            "total_gas_used":
                self.total_gas_used,

            "average_execution_time":
                self.average_execution_time,
        }