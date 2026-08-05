from influx.execution.state_machine import (
    StateMachine,
)

from influx.execution.transaction_executor import (
    TransactionExecutor,
)


class Transaction:

    transaction_id = "tx-1"

    sender = "alice"

    receiver = "bob"

    amount = 25



def test_execute_transaction():

    machine = StateMachine(
        {
            "alice": 100,
            "bob": 0,
        }
    )

    executor = TransactionExecutor(
        machine
    )

    result = executor.execute(
        Transaction()
    )

    assert result.success is True

    assert (
        machine.get("alice")
        == 75
    )

    assert (
        machine.get("bob")
        == 25
    )


def test_execution_result():

    machine = StateMachine()

    executor = TransactionExecutor(
        machine
    )

    result = executor.execute(
        Transaction()
    )

    assert (
        result.transaction_id
        == "tx-1"
    )


def test_failed_execution():

    class InvalidTransaction:
        transaction_id = "bad"

    machine = StateMachine()

    executor = TransactionExecutor(
        machine
    )

    result = executor.execute(
        InvalidTransaction()
    )

    assert result.success is False