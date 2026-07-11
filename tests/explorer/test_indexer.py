import pytest

from influx.explorer.indexer import (
    ExplorerIndexer,
)

from influx.explorer.blocks import (
    BlockRecord,
)

from influx.explorer.transactions import (
    TransactionRecord,
)

from influx.explorer.accounts import (
    AccountRecord,
)

from influx.explorer.exceptions import (
    IndexingError,
)


def create_indexer() -> ExplorerIndexer:
    return ExplorerIndexer()


def test_index_block() -> None:
    indexer = create_indexer()

    block = BlockRecord(
        height=1,
        block_hash="hash",
        previous_hash="prev",
        timestamp=100,
    )

    indexer.index_block(block)

    assert indexer.block_count() == 1


def test_index_transaction() -> None:
    indexer = create_indexer()

    transaction = TransactionRecord(
        tx_id="tx1",
        sender="alice",
        recipient="bob",
        amount=10,
    )

    indexer.index_transaction(transaction)

    assert indexer.transaction_count() == 1


def test_index_account() -> None:
    indexer = create_indexer()

    account = AccountRecord(
        address="wallet1",
    )

    indexer.index_account(account)

    assert indexer.account_count() == 1


def test_invalid_block_height() -> None:
    indexer = create_indexer()

    block = BlockRecord(
        height=-1,
        block_hash="bad",
        previous_hash="prev",
        timestamp=0,
    )

    with pytest.raises(IndexingError):
        indexer.index_block(block)


def test_missing_transaction_id() -> None:
    indexer = create_indexer()

    transaction = TransactionRecord(
        tx_id="",
        sender="alice",
        recipient="bob",
        amount=1,
    )

    with pytest.raises(IndexingError):
        indexer.index_transaction(transaction)