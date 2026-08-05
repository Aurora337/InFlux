from influx.contracts.scheduler.task import ContractExecutionTask


def create_task():
    return ContractExecutionTask(
        task_id="task_001",
        contract_id="contract_001",
        operation="execute",
        priority=10,
    )


def test_task_creation():

    task = create_task()

    assert task.task_id == "task_001"


def test_task_serialization():

    task = create_task()

    exported = task.to_dict()

    assert exported["contract_id"] == "contract_001"


def test_task_operation():

    task = create_task()

    assert task.operation == "execute"


def test_priority_comparison():

    high = create_task()

    low = ContractExecutionTask(
        task_id="task_002",
        contract_id="contract_002",
        operation="execute",
        priority=1,
    )

    assert high.higher_priority_than(low)


def test_task_determinism():

    first = create_task()
    second = create_task()

    assert first.to_dict() == second.to_dict()


def test_task_immutability():

    task = create_task()

    try:
        task.priority = 20
    except Exception:
        assert True
    else:
        assert False