from influx.mempool.queue import (
    PendingTransaction,
)

from influx.mempool.prioritizer import (
    TransactionPrioritizer,
)


def create_transaction(
    tx_id: str,
    fee: int,
) -> PendingTransaction:

    return PendingTransaction(
        tx_id=tx_id,
        payload={
            "amount": 100,
        },
        fee=fee,
    )


def test_priority_ordering():

    prioritizer = TransactionPrioritizer()

    transactions = [
        create_transaction(
            "tx-low",
            1,
        ),
        create_transaction(
            "tx-high",
            100,
        ),
        create_transaction(
            "tx-medium",
            50,
        ),
    ]

    result = prioritizer.prioritize(
        transactions
    )

    assert (
        result[0].tx_id
        == "tx-high"
    )

    assert (
        result[1].tx_id
        == "tx-medium"
    )

    assert (
        result[2].tx_id
        == "tx-low"
    )


def test_priority_score():

    prioritizer = TransactionPrioritizer()

    transaction = create_transaction(
        "tx-1",
        25,
    )

    assert (
        prioritizer.priority_score(
            transaction
        )
        == 25
    )