from influx.contracts.scheduler.order import ExecutionOrder
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


def test_order_creation():

    order = ExecutionOrder.from_task(
        create_task()
    )

    assert order.task_id == "task_001"


def test_order_priority():

    high = ExecutionOrder.from_task(
        create_task("high", 10)
    )

    low = ExecutionOrder.from_task(
        create_task("low", 1)
    )

    assert high.before(low)


def test_equal_priority_uses_identifier():

    first = ExecutionOrder.from_task(
        create_task("a", 5)
    )

    second = ExecutionOrder.from_task(
        create_task("b", 5)
    )

    assert first.before(second)


def test_reverse_identifier():

    first = ExecutionOrder.from_task(
        create_task("b", 5)
    )

    second = ExecutionOrder.from_task(
        create_task("a", 5)
    )

    assert not first.before(second)


def test_order_is_deterministic():

    first = ExecutionOrder.from_task(
        create_task()
    )

    second = ExecutionOrder.from_task(
        create_task()
    )

    assert first == second


def test_order_preserves_priority():

    order = ExecutionOrder.from_task(
        create_task(priority=20)
    )

    assert order.priority == 20