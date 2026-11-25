from __future__ import annotations

from dataclasses import dataclass, field

from .history import ContractExecutionHistory
from .record import ContractExecutionRecord
from .trace import ContractExecutionTrace


@dataclass(slots=True)
class ContractExecutionTracker:
    """
    Deterministic contract execution tracker.
    """

    history: ContractExecutionHistory = field(
        default_factory=ContractExecutionHistory
    )

    traces: list[ContractExecutionTrace] = field(
        default_factory=list,
    )

    def add_trace(
        self,
        trace: ContractExecutionTrace,
    ) -> None:
        """
        Store execution trace.
        """

        self.traces.append(trace)

    def record(
        self,
        record: ContractExecutionRecord,
    ) -> None:
        """
        Store execution record.
        """

        self.history.add(record)

    def trace_count(self) -> int:
        """
        Return number of traces.
        """

        return len(self.traces)

    def record_count(self) -> int:
        """
        Return number of records.
        """

        return self.history.count()