from influx.explorer.transactions import (
    TransactionRecord,
)


def test_transaction_record_creation() -> None:
    transaction = TransactionRecord(
        tx_id="tx1",
        sender="alice",
        recipient="bob",
        amount=100,
        block_height=5,
        confirmed=True,
    )

    assert transaction.tx_id == "tx1"
    assert transaction.sender == "alice"
    assert transaction.amount == 100
    assert transaction.confirmed is True