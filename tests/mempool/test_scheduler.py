from influx.mempool.transaction import Transaction
from influx.mempool.transaction_scheduler import (
    TransactionScheduler,
)


def create_transaction(
    tx_id,
    fee,
    nonce,
):

    return Transaction(
        transaction_id=tx_id,
        sender="alice",
        receiver="bob",
        amount=10,
        fee=fee,
        nonce=nonce,
        payload={},
    )


def test_sort_fee_priority():

    transactions = [
        create_transaction(
            "tx-low",
            1,
            1,
        ),
        create_transaction(
            "tx-high",
            10,
            1,
        ),
    ]

    ordered = TransactionScheduler.sort(
        transactions
    )

    assert (
        ordered[0].transaction_id
        == "tx-high"
    )


def test_sort_nonce_priority():

    transactions = [
        create_transaction(
            "tx-two",
            5,
            2,
        ),
        create_transaction(
            "tx-one",
            5,
            1,
        ),
    ]

    ordered = TransactionScheduler.sort(
        transactions
    )

    assert (
        ordered[0].transaction_id
        == "tx-one"
    )


def test_select_limit():

    transactions = [
        create_transaction(
            "tx-1",
            1,
            1,
        ),
        create_transaction(
            "tx-2",
            2,
            1,
        ),
    ]

    selected = TransactionScheduler.select(
        transactions,
        1,
    )

    assert len(selected) == 1


def test_schedule():

    transactions = [
        create_transaction(
            "tx-1",
            1,
            1,
        ),
    ]

    scheduled = TransactionScheduler.schedule(
        transactions
    )

    assert (
        scheduled[0].state.value
        == "scheduled"
    )