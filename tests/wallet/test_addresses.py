from influx.wallet.addresses import (
    AddressManager,
)


def test_address_generation():

    manager = AddressManager()

    address = manager.generate(
        account_id="account-1",
        public_key="public-key",
        created_at=100,
    )

    assert (
        address.account_id
        == "account-1"
    )

    assert (
        len(address.address)
        == 64
    )


def test_address_determinism():

    manager = AddressManager()

    first = manager.generate(
        "account-1",
        "public-key",
        100,
    )

    second = manager.generate(
        "account-1",
        "public-key",
        100,
    )

    assert (
        first.address
        == second.address
    )


def test_address_validation():

    manager = AddressManager()

    address = manager.generate(
        "account-1",
        "public-key",
        100,
    )

    assert (
        manager.validate(
            address
        )
        is True
    )