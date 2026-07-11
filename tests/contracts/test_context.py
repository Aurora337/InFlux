from influx.contracts.context import ExecutionContext


def test_execution_context() -> None:
    context = ExecutionContext(
        block_height=100,
        transaction_id="tx-1",
        caller="alice",
        network_id="ifx-main",
    )

    assert context.block_height == 100
    assert context.transaction_id == "tx-1"
    assert context.caller == "alice"
    assert context.network_id == "ifx-main"