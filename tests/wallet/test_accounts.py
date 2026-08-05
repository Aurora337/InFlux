from influx.wallet.accounts import (
    WalletAccount,
)


def test_wallet_account_creation():

    account = WalletAccount(
        account_id="account-1",
        identity_id="identity-1",
        created_at=100,
    )

    assert (
        account.account_id
        == "account-1"
    )

    assert (
        account.identity_id
        == "identity-1"
    )

    assert (
        account.active
        is True
    )


def test_add_address():

    account = WalletAccount(
        account_id="account-1",
        identity_id="identity-1",
        created_at=100,
    )

    account.add_address(
        "address-1"
    )

    assert (
        "address-1"
        in account.addresses
    )


def test_remove_address():

    account = WalletAccount(
        account_id="account-1",
        identity_id="identity-1",
        created_at=100,
    )

    account.add_address(
        "address-1"
    )

    removed = account.remove_address(
        "address-1"
    )

    assert removed is True

    assert (
        len(account.addresses)
        == 0
    )


def test_account_serialization():

    account = WalletAccount(
        account_id="account-1",
        identity_id="identity-1",
        created_at=100,
    )

    data = account.to_dict()

    assert (
        data["account_id"]
        == "account-1"
    )