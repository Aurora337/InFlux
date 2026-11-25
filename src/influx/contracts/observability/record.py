from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ContractExecutionRecord:
    """
    Immutable deterministic execution record.
    """

    record_id: str
    trace_id: str
    executor: str
    sequence: int

    def to_dict(self) -> dict[str, Any]:
        """
        Return deterministic record representation.
        """
        return {
            "record_id": self.record_id,
            "trace_id": self.trace_id,
            "executor": self.executor,
            "sequence": self.sequence,
        }

    def follows(
        self,
        previous: "ContractExecutionRecord",
    ) -> bool:
        """
        Determine whether this record follows another record.
        """
        return self.sequence > previous.sequence