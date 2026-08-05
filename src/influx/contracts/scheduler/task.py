from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ContractExecutionTask:
    """
    Immutable deterministic contract execution task.
    """

    task_id: str
    contract_id: str
    operation: str
    priority: int

    def to_dict(self) -> dict[str, Any]:
        """
        Return deterministic task representation.
        """
        return {
            "task_id": self.task_id,
            "contract_id": self.contract_id,
            "operation": self.operation,
            "priority": self.priority,
        }

    def higher_priority_than(
        self,
        other: "ContractExecutionTask",
    ) -> bool:
        """
        Compare task priority.
        """
        return self.priority > other.priority