import pytest

from influx.sdk.client import InFluxClient
from influx.sdk.exceptions import RPCRequestError
from influx.sdk.wallet import WalletClient


def connected_wallet() -> WalletClient:
    client = InFluxClient()
    client.connect()
    return WalletClient(client)


def test_get_balance() -> None:
    wallet = connected_wallet()

    response = wallet.get_balance("wallet-1")

    assert response.success is True

    balance = response.result

    assert balance is not None
    assert balance.address == "wallet-1"


def test_build_transaction() -> None:
    wallet = connected_wallet()

    request = wallet.build_transaction(
        sender="alice",
        recipient="bob",
        amount=100,
        fee=1,
    )

    assert request.sender == "alice"
    assert request.recipient == "bob"
    assert request.amount == 100
    assert request.fee == 1


def test_sign_transaction() -> None:
    wallet = connected_wallet()

    request = wallet.build_transaction(
        sender="alice",
        recipient="bob",
        amount=25,
    )

    signed = wallet.sign_transaction(
        request,
        signature="signed",
    )

    assert signed.request == request
    assert signed.signature == "signed"
    assert signed.tx_id


def test_wallet_requires_connection() -> None:
    client = InFluxClient()

    wallet = WalletClient(client)

    with pytest.raises(RPCRequestError):
        wallet.get_balance("wallet-1")