from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ContractExecutionTrace:
    """
    Immutable deterministic contract execution trace.
    """

    trace_id: str
    contract_id: str
    operation: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        """
        Return deterministic trace representation.
        """
        return {
            "trace_id": self.trace_id,
            "contract_id": self.contract_id,
            "operation": self.operation,
            "status": self.status,
        }

    def is_complete(self) -> bool:
        """
        Determine whether execution completed successfully.
        """
        return self.status == "completed"