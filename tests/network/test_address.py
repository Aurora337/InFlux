from influx.network.address import NetworkAddress
from influx.network.errors import AddressError

import pytest


def test_endpoint() -> None:
    address = NetworkAddress(
        host="127.0.0.1",
        port=8080,
    )

    assert address.endpoint == "127.0.0.1:8080"


def test_validate_success() -> None:
    address = NetworkAddress(
        host="localhost",
        port=9000,
    )

    address.validate()


def test_invalid_host() -> None:
    with pytest.raises(AddressError):
        NetworkAddress(
            host="",
            port=9000,
        ).validate()


def test_invalid_port() -> None:
    with pytest.raises(AddressError):
        NetworkAddress(
            host="localhost",
            port=0,
        ).validate()