from influx.block.block_scheduler import (
    BlockScheduler,
)

from influx.mempool.transaction import (
    Transaction,
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


def test_fee_priority():

    transactions = [
        create_transaction(
            "low",
            1,
            1,
        ),
        create_transaction(
            "high",
            10,
            1,
        ),
    ]

    ordered = BlockScheduler.order(
        transactions
    )

    assert (
        ordered[0].transaction_id
        == "high"
    )


def test_nonce_priority():

    transactions = [
        create_transaction(
            "later",
            5,
            2,
        ),
        create_transaction(
            "first",
            5,
            1,
        ),
    ]

    ordered = BlockScheduler.order(
        transactions
    )

    assert (
        ordered[0].transaction_id
        == "first"
    )


def test_selection_limit():

    transactions = [
        create_transaction(
            "one",
            1,
            1,
        ),
        create_transaction(
            "two",
            2,
            1,
        ),
    ]

    selected = BlockScheduler.select(
        transactions,
        1,
    )

    assert len(selected) == 1