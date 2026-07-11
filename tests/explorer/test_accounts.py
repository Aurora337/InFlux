from influx.explorer.accounts import (
    AccountRecord,
)


def test_account_record_creation() -> None:
    account = AccountRecord(
        address="wallet1",
        balance=500,
        transaction_count=3,
        transaction_ids=[
            "tx1",
            "tx2",
        ],
    )

    assert account.address == "wallet1"
    assert account.balance == 500
    assert account.transaction_count == 3
    assert len(account.transaction_ids) == 2