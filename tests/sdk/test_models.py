from influx.sdk.models import (
    AccountBalance,
    NetworkInfo,
    RPCResponse,
    TransactionReceipt,
)


def test_rpc_response() -> None:
    response = RPCResponse(
        success=True,
        result="ok",
    )

    assert response.success is True
    assert response.result == "ok"
    assert response.error is None


def test_network_info() -> None:
    info = NetworkInfo(
        chain_id="influx",
        protocol_version="1.0",
        peer_count=5,
        block_height=100,
    )

    assert info.chain_id == "influx"
    assert info.peer_count == 5


def test_account_balance() -> None:
    balance = AccountBalance(
        address="wallet1",
        confirmed=100,
        pending=5,
    )

    assert balance.confirmed == 100
    assert balance.pending == 5


def test_transaction_receipt() -> None:
    receipt = TransactionReceipt(
        tx_id="abc123",
        accepted=True,
        message="accepted",
    )

    assert receipt.accepted is True
    assert receipt.tx_id == "abc123"