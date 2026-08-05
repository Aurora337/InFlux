from influx.runtime.context import ExecutionContext
from influx.runtime.errors import ContextError


def test_context_storage() -> None:
    context = ExecutionContext(
        transaction_id="tx-1",
        caller="alice",
    )

    context.set_value(
        "balance",
        100,
    )

    assert context.get_value("balance") == 100


def test_context_default_value() -> None:
    context = ExecutionContext(
        transaction_id="tx-1",
        caller="alice",
    )

    assert context.get_value("missing") is None


def test_context_empty_key_rejected() -> None:
    context = ExecutionContext(
        transaction_id="tx-1",
        caller="alice",
    )

    try:
        context.set_value("", 1)
    except ContextError:
        assert True
    else:
        assert False


def test_context_logs() -> None:
    context = ExecutionContext(
        transaction_id="tx-1",
        caller="alice",
    )

    context.emit_log("executed")

    assert context.logs == ["executed"]