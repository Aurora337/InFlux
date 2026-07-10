from influx.mempool.transaction import Transaction
from influx.mempool.transaction_pool import TransactionPool


def create_transaction(
    transaction_id="tx-1",
):

    return Transaction(
        transaction_id=transaction_id,
        sender="alice",
        receiver="bob",
        amount=50,
        fee=2,
        nonce=1,
        payload={},
    )


def test_add():

    pool = TransactionPool()

    assert pool.add(
        create_transaction()
    )

    assert pool.size() == 1


def test_duplicate():

    pool = TransactionPool()

    tx = create_transaction()

    pool.add(tx)

    assert not pool.add(tx)


def test_lookup():

    pool = TransactionPool()

    tx = create_transaction()

    pool.add(tx)

    result = pool.lookup(
        "tx-1"
    )

    assert result is tx


def test_remove():

    pool = TransactionPool()

    pool.add(
        create_transaction()
    )

    assert pool.remove(
        "tx-1"
    )

    assert pool.size() == 0


def test_remove_missing():

    pool = TransactionPool()

    assert not pool.remove(
        "missing"
    )


def test_pending():

    pool = TransactionPool()

    pool.add(
        create_transaction()
    )

    pending = pool.pending()

    assert len(pending) == 1


def test_snapshot():

    pool = TransactionPool()

    pool.add(
        create_transaction()
    )

    snapshot = pool.snapshot()

    assert "tx-1" in snapshot