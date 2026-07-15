from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeMetrics:
    """
    Runtime execution metrics.

    Tracks deterministic runtime activity for
    monitoring and diagnostics.
    """

    dispatched: int = 0
    executed: int = 0
    failed: int = 0

    def record_dispatch(self) -> None:
        """
        Record a dispatched task.
        """

        self.dispatched += 1

    def record_execution(self) -> None:
        """
        Record a completed execution.
        """

        self.executed += 1

    def record_failure(self) -> None:
        """
        Record a failed execution.
        """

        self.failed += 1

    def reset(self) -> None:
        """
        Reset all runtime metrics.
        """

        self.dispatched = 0
        self.executed = 0
        self.failed = 0