from influx.sdk.transactions import (
    SignedTransaction,
    TransactionRequest,
)


def test_transaction_request() -> None:
    request = TransactionRequest(
        sender="alice",
        recipient="bob",
        amount=100,
        fee=2,
    )

    assert request.sender == "alice"
    assert request.recipient == "bob"
    assert request.amount == 100
    assert request.fee == 2


def test_signed_transaction() -> None:
    request = TransactionRequest(
        sender="alice",
        recipient="bob",
        amount=50,
    )

    signed = SignedTransaction(
        tx_id="tx-001",
        request=request,
        signature="signature",
    )

    assert signed.tx_id == "tx-001"
    assert signed.request == request
    assert signed.signature == "signature"