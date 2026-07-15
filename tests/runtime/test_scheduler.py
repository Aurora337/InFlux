from influx.runtime.queue import (
    RuntimeQueue,
    RuntimeTask,
)
from influx.runtime.scheduler import RuntimeScheduler


def test_schedule_task() -> None:
    queue = RuntimeQueue()
    scheduler = RuntimeScheduler(queue)

    task = RuntimeTask(
        task_id="task-1",
        payload={},
    )

    scheduler.schedule(task)

    assert scheduler.pending() == 1


def test_execute_task() -> None:
    queue = RuntimeQueue()
    scheduler = RuntimeScheduler(queue)

    task = RuntimeTask(
        task_id="task-1",
        payload={},
    )

    scheduler.schedule(task)

    result = scheduler.next_task()

    assert result == task
    assert scheduler.stats.executed == 1