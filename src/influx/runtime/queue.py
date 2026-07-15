from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RuntimeTask:
    """
    Deterministic runtime task.
    """

    task_id: str
    payload: dict[str, Any]


class RuntimeQueue:
    """
    FIFO runtime execution queue.
    """

    def __init__(self) -> None:
        self._tasks: list[RuntimeTask] = []

    def push(
        self,
        task: RuntimeTask,
    ) -> None:
        """
        Add task to queue.
        """

        self._tasks.append(task)

    def pop(
        self,
    ) -> RuntimeTask | None:
        """
        Remove next task.
        """

        if not self._tasks:
            return None

        return self._tasks.pop(0)

    def size(
        self,
    ) -> int:
        """
        Return queue size.
        """

        return len(self._tasks)

    def empty(
        self,
    ) -> bool:
        """
        Check if queue is empty.
        """

        return not self._tasks