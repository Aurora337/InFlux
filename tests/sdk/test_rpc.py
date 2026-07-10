import pytest

from influx.sdk.client import InFluxClient
from influx.sdk.rpc import RPCClient
from influx.sdk.transactions import (
    SignedTransaction,
    TransactionRequest,
)
from influx.sdk.exceptions import (
    RPCRequestError,
)


def connected_rpc() -> RPCClient:
    client = InFluxClient()
    client.connect()
    return RPCClient(client)


def test_get_network_info() -> None:
    rpc = connected_rpc()

    response = rpc.get_network_info()

    assert response.success is True

    info = response.result

    assert info is not None
    assert info.chain_id == "influx"


def test_submit_transaction() -> None:
    rpc = connected_rpc()

    request = TransactionRequest(
        sender="alice",
        recipient="bob",
        amount=10,
    )

    signed = SignedTransaction(
        tx_id="tx-123",
        request=request,
        signature="sig",
    )

    response = rpc.submit_transaction(signed)

    assert response.success is True

    receipt = response.result

    assert receipt is not None
    assert receipt.accepted is True


def test_rpc_requires_connection() -> None:
    client = InFluxClient()

    rpc = RPCClient(client)

    with pytest.raises(RPCRequestError):
        rpc.get_network_info()