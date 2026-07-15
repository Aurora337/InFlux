from __future__ import annotations

from dataclasses import dataclass

from .queue import RuntimeQueue, RuntimeTask


@dataclass(slots=True)
class RuntimeSchedulerStats:
    """
    Scheduler execution metrics.
    """

    scheduled: int = 0
    executed: int = 0


class RuntimeScheduler:
    """
    Deterministic runtime task scheduler.
    """

    def __init__(
        self,
        queue: RuntimeQueue,
    ) -> None:
        self.queue = queue
        self.stats = RuntimeSchedulerStats()

    def schedule(
        self,
        task: RuntimeTask,
    ) -> None:
        """
        Add task to execution queue.
        """

        self.queue.push(task)
        self.stats.scheduled += 1

    def pending(
        self,
    ) -> int:
        """
        Return number of queued tasks.
        """

        return self.queue.size()

    def next_task(
        self,
    ) -> RuntimeTask | None:
        """
        Retrieve next task.
        """

        task = self.queue.pop()

        if task is not None:
            self.stats.executed += 1

        return task

    def next_batch(
        self,
        limit: int = 1,
    ) -> list[RuntimeTask]:
        """
        Retrieve next scheduled tasks.
        """

        tasks: list[RuntimeTask] = []

        while len(tasks) < limit:
            task = self.next_task()

            if task is None:
                break

            tasks.append(task)

        return tasks