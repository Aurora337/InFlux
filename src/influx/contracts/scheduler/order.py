from __future__ import annotations

from dataclasses import dataclass

from .task import ContractExecutionTask


@dataclass(frozen=True, slots=True)
class ExecutionOrder:
    """
    Deterministic execution ordering definition.
    """

    task_id: str
    priority: int

    @classmethod
    def from_task(
        cls,
        task: ContractExecutionTask,
    ) -> "ExecutionOrder":
        """
        Create ordering record from a task.
        """

        return cls(
            task_id=task.task_id,
            priority=task.priority,
        )

    def before(
        self,
        other: "ExecutionOrder",
    ) -> bool:
        """
        Determine deterministic ordering position.
        """

        if self.priority != other.priority:
            return self.priority > other.priority

        return self.task_id < other.task_id