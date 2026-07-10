from influx.mempool.queue import (
    PendingTransaction,
    TransactionQueue,
)

from influx.mempool.eviction import (
    TransactionEvictor,
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


def test_evict_lowest_fee():

    queue = TransactionQueue()

    queue.add(
        create_transaction(
            "tx-low",
            1,
        )
    )

    queue.add(
        create_transaction(
            "tx-high",
            100,
        )
    )

    evictor = TransactionEvictor()

    removed = evictor.evict_lowest_fee(
        queue
    )

    assert removed is not None

    assert (
        removed.tx_id
        == "tx-low"
    )

    assert (
        queue.contains(
            "tx-low"
        )
        is False
    )


def test_empty_eviction():

    queue = TransactionQueue()

    evictor = TransactionEvictor()

    removed = evictor.evict_lowest_fee(
        queue
    )

    assert removed is None


def test_capacity_enforcement():

    queue = TransactionQueue()

    queue.add(
        create_transaction(
            "tx-1",
            1,
        )
    )

    queue.add(
        create_transaction(
            "tx-2",
            2,
        )
    )

    queue.add(
        create_transaction(
            "tx-3",
            3,
        )
    )

    evictor = TransactionEvictor()

    removed = evictor.enforce_capacity(
        queue,
        2,
    )

    assert len(
        removed
    ) == 1

    assert (
        queue.size()
        == 2
    )