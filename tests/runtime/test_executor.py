from influx.runtime.context import ExecutionContext
from influx.runtime.executor import RuntimeExecutor
from influx.runtime.errors import ExecutionError


def test_execute_operation() -> None:
    executor = RuntimeExecutor()

    context = ExecutionContext(
        transaction_id="tx-1",
        caller="alice",
    )

    def operation(ctx: ExecutionContext) -> str:
        ctx.emit_log("done")
        return "success"

    result = executor.execute(
        context,
        operation,
    )

    assert result == "success"
    assert executor.execution_count() == 1
    assert context.logs == ["done"]


def test_missing_transaction_id() -> None:
    executor = RuntimeExecutor()

    context = ExecutionContext(
        transaction_id="",
        caller="alice",
    )

    def operation(ctx: ExecutionContext) -> None:
        pass

    try:
        executor.execute(
            context,
            operation,
        )
    except ExecutionError:
        assert True
    else:
        assert False


def test_operation_failure() -> None:
    executor = RuntimeExecutor()

    context = ExecutionContext(
        transaction_id="tx-1",
        caller="alice",
    )

    def operation(ctx: ExecutionContext) -> None:
        raise ValueError("failed")

    try:
        executor.execute(
            context,
            operation,
        )
    except ExecutionError:
        assert True
    else:
        assert False