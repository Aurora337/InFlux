from influx.block.block_builder import (
    BlockBuilder,
)

from influx.mempool.transaction import (
    Transaction,
)


def create_transaction(
    tx_id,
    fee,
):

    return Transaction(
        transaction_id=tx_id,
        sender="alice",
        receiver="bob",
        amount=10,
        fee=fee,
        nonce=1,
        payload={},
    )


def test_builder_creates_block():

    builder = BlockBuilder(
        proposer="node-a"
    )

    block = builder.build(
        transactions=[],
        previous_hash="previous",
        height=1,
    )

    assert (
        block.header.height
        == 1
    )

    assert (
        block.header.previous_hash
        == "previous"
    )


def test_builder_assigns_proposer():

    builder = BlockBuilder(
        proposer="node-a"
    )

    block = builder.build(
        transactions=[],
        previous_hash="hash",
        height=5,
    )

    assert (
        block.header.proposer
        == "node-a"
    )


def test_builder_limits_transactions():

    builder = BlockBuilder(
        proposer="node-a",
        max_transactions=1,
    )

    transactions = [
        create_transaction(
            "tx-1",
            1,
        ),
        create_transaction(
            "tx-2",
            2,
        ),
    ]

    block = builder.build(
        transactions=transactions,
        previous_hash="hash",
        height=1,
    )

    assert len(
        block.transactions
    ) == 1


def test_builder_orders_transactions():

    builder = BlockBuilder(
        proposer="node-a"
    )

    transactions = [
        create_transaction(
            "low",
            1,
        ),
        create_transaction(
            "high",
            10,
        ),
    ]

    block = builder.build(
        transactions=transactions,
        previous_hash="hash",
        height=1,
    )

    assert (
        block.transactions[0].transaction_id
        == "high"
    )