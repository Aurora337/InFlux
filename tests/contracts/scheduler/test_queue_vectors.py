from influx.contracts.scheduler.queue import ContractExecutionQueue
from influx.contracts.scheduler.task import ContractExecutionTask


def create_task(
    task_id="task_001",
    priority=10,
):
    return ContractExecutionTask(
        task_id=task_id,
        contract_id="contract_001",
        operation="execute",
        priority=priority,
    )


def test_queue_add():

    queue = ContractExecutionQueue()

    queue.add(create_task())

    assert queue.size() == 1


def test_queue_ordering():

    queue = ContractExecutionQueue()

    queue.add(create_task("low", 1))
    queue.add(create_task("high", 10))

    ordered = queue.ordered()

    assert ordered[0].task_id == "high"


def test_queue_lookup():

    queue = ContractExecutionQueue()

    queue.add(create_task())

    assert queue.get("task_001") is not None


def test_missing_task():

    queue = ContractExecutionQueue()

    assert queue.get("missing") is None


def test_queue_remove():

    queue = ContractExecutionQueue()

    queue.add(create_task())

    queue.remove("task_001")

    assert queue.size() == 0


def test_queue_deterministic():

    queue = ContractExecutionQueue()

    queue.add(create_task("b", 5))
    queue.add(create_task("a", 5))

    ordered = queue.ordered()

    assert ordered[0].task_id == "a"