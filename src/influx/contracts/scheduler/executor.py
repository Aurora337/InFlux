from __future__ import annotations

from dataclasses import dataclass, field

from .queue import ContractExecutionQueue
from .task import ContractExecutionTask


@dataclass(slots=True)
class ContractExecutionExecutor:
    """
    Deterministic contract execution coordinator.
    """

    queue: ContractExecutionQueue = field(
        default_factory=ContractExecutionQueue
    )

    executed: list[str] = field(
        default_factory=list,
    )

    def submit(
        self,
        task: ContractExecutionTask,
    ) -> None:
        """
        Submit a task for execution.
        """

        self.queue.add(task)

    def next_task(
        self,
    ) -> ContractExecutionTask | None:
        """
        Retrieve next deterministic task.
        """

        ordered = self.queue.ordered()

        if not ordered:
            return None

        return ordered[0]

    def execute_next(
        self,
    ) -> ContractExecutionTask | None:
        """
        Execute the next scheduled task.
        """

        task = self.next_task()

        if task is None:
            return None

        self.queue.remove(
            task.task_id,
        )

        self.executed.append(
            task.task_id,
        )

        return task

    def execution_count(self) -> int:
        """
        Return completed execution count.
        """

        return len(self.executed)