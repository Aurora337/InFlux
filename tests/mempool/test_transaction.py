from influx.mempool.transaction import Transaction
from influx.mempool.transaction_state import TransactionState


def create_transaction():

    return Transaction(
        transaction_id="tx-1",
        sender="alice",
        receiver="bob",
        amount=100,
        fee=5,
        nonce=1,
        payload={
            "message": "hello"
        },
    )


def test_defaults():

    tx = create_transaction()

    assert tx.transaction_id == "tx-1"
    assert tx.sender == "alice"
    assert tx.receiver == "bob"
    assert tx.amount == 100
    assert tx.fee == 5
    assert tx.nonce == 1

    assert (
        tx.state
        == TransactionState.CREATED
    )


def test_validate():

    tx = create_transaction()

    tx.validate()

    assert (
        tx.state
        == TransactionState.VALIDATING
    )


def test_mark_valid():

    tx = create_transaction()

    tx.mark_valid()

    assert (
        tx.state
        == TransactionState.VALID
    )


def test_schedule():

    tx = create_transaction()

    tx.schedule()

    assert (
        tx.state
        == TransactionState.SCHEDULED
    )


def test_execute():

    tx = create_transaction()

    tx.execute()

    assert (
        tx.state
        == TransactionState.EXECUTED
    )


def test_drop():

    tx = create_transaction()

    tx.drop()

    assert (
        tx.state
        == TransactionState.DROPPED
    )


def test_snapshot():

    tx = create_transaction()

    snapshot = tx.snapshot()

    assert snapshot["transaction_id"] == "tx-1"
    assert snapshot["sender"] == "alice"
    assert snapshot["receiver"] == "bob"
    assert snapshot["amount"] == 100
    assert snapshot["fee"] == 5
    assert snapshot["nonce"] == 1
    assert snapshot["state"] == "created"