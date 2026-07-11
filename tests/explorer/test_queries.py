from influx.explorer.queries import (
    BlockQueryResult,
    TransactionQueryResult,
    AccountQueryResult,
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


def test_block_query_result() -> None:
    block = BlockRecord(
        height=1,
        block_hash="hash",
        previous_hash="prev",
        timestamp=1,
    )

    result = BlockQueryResult(
        block=block,
    )

    assert result.block.height == 1


def test_transaction_query_result() -> None:
    transaction = TransactionRecord(
        tx_id="tx1",
        sender="alice",
        recipient="bob",
        amount=25,
    )

    result = TransactionQueryResult(
        transaction=transaction,
    )

    assert result.transaction.tx_id == "tx1"


def test_account_query_result() -> None:
    account = AccountRecord(
        address="wallet",
        balance=100,
    )

    result = AccountQueryResult(
        account=account,
    )

    assert result.account.address == "wallet"