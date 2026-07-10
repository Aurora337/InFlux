from influx.execution.execution_metrics import (
    ExecutionMetrics,
)


def test_success_record():

    metrics = ExecutionMetrics()

    metrics.record_success(
        gas_used=5
    )

    assert (
        metrics.successful_executions
        == 1
    )

    assert (
        metrics.total_gas_used
        == 5
    )


def test_failure_record():

    metrics = ExecutionMetrics()

    metrics.record_failure()

    assert (
        metrics.failed_executions
        == 1
    )


def test_block_record():

    metrics = ExecutionMetrics()

    metrics.record_block()

    assert (
        metrics.blocks_executed
        == 1
    )


def test_execution_time():

    metrics = ExecutionMetrics()

    metrics.update_execution_time(
        10
    )

    metrics.update_execution_time(
        20
    )

    assert (
        metrics.average_execution_time
        == 15
    )


def test_snapshot():

    metrics = ExecutionMetrics()

    snapshot = metrics.snapshot()

    assert (
        "transactions_executed"
        in snapshot
    )

    assert (
        "total_gas_used"
        in snapshot
    )