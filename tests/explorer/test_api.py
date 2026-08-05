import pytest

from influx.explorer.api import ExplorerAPI
from influx.explorer.indexer import ExplorerIndexer
from influx.explorer.blocks import BlockRecord
from influx.explorer.transactions import TransactionRecord
from influx.explorer.accounts import AccountRecord
from influx.explorer.exceptions import (
    RecordNotFoundError,
)


def create_api() -> ExplorerAPI:
    indexer = ExplorerIndexer()

    indexer.index_block(
        BlockRecord(
            height=1,
            block_hash="block1",
            previous_hash="genesis",
            timestamp=100,
        )
    )

    indexer.index_transaction(
        TransactionRecord(
            tx_id="tx1",
            sender="alice",
            recipient="bob",
            amount=50,
        )
    )

    indexer.index_account(
        AccountRecord(
            address="wallet1",
            balance=500,
        )
    )

    return ExplorerAPI(indexer)


def test_get_block() -> None:
    api = create_api()

    result = api.get_block(1)

    assert result.block.block_hash == "block1"


def test_get_transaction() -> None:
    api = create_api()

    result = api.get_transaction("tx1")

    assert result.transaction.amount == 50


def test_get_account() -> None:
    api = create_api()

    result = api.get_account("wallet1")

    assert result.account.balance == 500


def test_missing_block() -> None:
    api = create_api()

    with pytest.raises(RecordNotFoundError):
        api.get_block(99)


def test_missing_transaction() -> None:
    api = create_api()

    with pytest.raises(RecordNotFoundError):
        api.get_transaction("missing")


def test_missing_account() -> None:
    api = create_api()

    with pytest.raises(RecordNotFoundError):
        api.get_account("unknown")