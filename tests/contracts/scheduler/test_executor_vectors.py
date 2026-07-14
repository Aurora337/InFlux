from influx.contracts.scheduler.executor import (
    ContractExecutionExecutor,
)
from influx.contracts.scheduler.task import (
    ContractExecutionTask,
)


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


def test_submit_task():

    executor = ContractExecutionExecutor()

    executor.submit(
        create_task()
    )

    assert executor.queue.size() == 1


def test_next_task():

    executor = ContractExecutionExecutor()

    executor.submit(
        create_task()
    )

    assert executor.next_task().task_id == "task_001"


def test_priority_execution():

    executor = ContractExecutionExecutor()

    executor.submit(
        create_task("low", 1)
    )

    executor.submit(
        create_task("high", 10)
    )

    assert executor.next_task().task_id == "high"


def test_execute_next():

    executor = ContractExecutionExecutor()

    executor.submit(
        create_task()
    )

    result = executor.execute_next()

    assert result.task_id == "task_001"


def test_execution_tracking():

    executor = ContractExecutionExecutor()

    executor.submit(
        create_task()
    )

    executor.execute_next()

    assert executor.execution_count() == 1


def test_empty_execution():

    executor = ContractExecutionExecutor()

    assert executor.execute_next() is None