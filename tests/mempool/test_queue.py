import pytest

from influx.mempool.queue import (
    PendingTransaction,
    TransactionQueue,
)

from influx.mempool.exceptions import (
    InvalidTransactionError,
    DuplicateTransactionError,
    TransactionNotFoundError,
)


def create_transaction(
    tx_id: str = "tx-1",
    fee: int = 10,
) -> PendingTransaction:

    return PendingTransaction(
        tx_id=tx_id,
        payload={
            "amount": 100,
        },
        fee=fee,
    )


def test_add_transaction():

    queue = TransactionQueue()

    transaction = create_transaction()

    queue.add(
        transaction
    )

    assert (
        queue.contains(
            "tx-1"
        )
        is True
    )


def test_get_transaction():

    queue = TransactionQueue()

    transaction = create_transaction()

    queue.add(
        transaction
    )

    result = queue.get(
        "tx-1"
    )

    assert (
        result
        == transaction
    )


def test_remove_transaction():

    queue = TransactionQueue()

    queue.add(
        create_transaction()
    )

    removed = queue.remove(
        "tx-1"
    )

    assert removed is True

    assert (
        queue.contains(
            "tx-1"
        )
        is False
    )


def test_duplicate_transaction():

    queue = TransactionQueue()

    transaction = create_transaction()

    queue.add(
        transaction
    )

    with pytest.raises(
        DuplicateTransactionError
    ):

        queue.add(
            transaction
        )


def test_invalid_transaction():

    queue = TransactionQueue()

    transaction = PendingTransaction(
        tx_id="",
        payload={},
    )

    with pytest.raises(
        InvalidTransactionError
    ):

        queue.add(
            transaction
        )


def test_missing_transaction():

    queue = TransactionQueue()

    with pytest.raises(
        TransactionNotFoundError
    ):

        queue.get(
            "missing"
        )


def test_queue_size():

    queue = TransactionQueue()

    queue.add(
        create_transaction()
    )

    assert (
        queue.size()
        == 1
    )