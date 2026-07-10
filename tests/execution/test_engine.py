from influx.execution.execution_engine import (
    ExecutionEngine,
)


class Transaction:

    transaction_id = "tx-1"

    sender = "alice"

    receiver = "bob"

    amount = 10


class Block:

    transactions = [
        Transaction(),
        Transaction(),
    ]



def test_execute_transaction():

    engine = ExecutionEngine()

    result = engine.execute_transaction(
        Transaction()
    )

    assert result.success is True


def test_execute_block():

    engine = ExecutionEngine()

    results = engine.execute_block(
        Block()
    )

    assert (
        len(results)
        == 2
    )

    assert (
        results[0].success
        is True
    )


def test_snapshot():

    engine = ExecutionEngine()

    snapshot = engine.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )