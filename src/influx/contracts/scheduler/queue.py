from __future__ import annotations

from dataclasses import dataclass, field

from .task import ContractExecutionTask


@dataclass(slots=True)
class ContractExecutionQueue:
    """
    Deterministic contract execution queue.
    """

    tasks: list[ContractExecutionTask] = field(
        default_factory=list,
    )

    def add(
        self,
        task: ContractExecutionTask,
    ) -> None:
        """
        Add a task to the queue.
        """
        self.tasks.append(task)

    def size(self) -> int:
        """
        Return queue size.
        """
        return len(self.tasks)

    def ordered(self) -> list[ContractExecutionTask]:
        """
        Return deterministic priority ordering.
        """

        return sorted(
            self.tasks,
            key=lambda task: (
                -task.priority,
                task.task_id,
            ),
        )

    def get(
        self,
        task_id: str,
    ) -> ContractExecutionTask | None:
        """
        Find task by identifier.
        """

        for task in self.tasks:
            if task.task_id == task_id:
                return task

        return None

    def remove(
        self,
        task_id: str,
    ) -> None:
        """
        Remove task from queue.
        """

        self.tasks = [
            task
            for task in self.tasks
            if task.task_id != task_id
        ]