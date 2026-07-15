from influx.runtime.queue import (
    RuntimeQueue,
    RuntimeTask,
)


def test_queue_push_pop() -> None:
    queue = RuntimeQueue()

    task = RuntimeTask(
        task_id="task-1",
        payload={"value": 1},
    )

    queue.push(task)

    assert queue.size() == 1

    result = queue.pop()

    assert result == task
    assert queue.empty()


def test_empty_queue() -> None:
    queue = RuntimeQueue()

    assert queue.pop() is None
    assert queue.size() == 0