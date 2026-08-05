from influx.wallet.transactions import (
    TransactionInput,
    TransactionOutput,
    WalletTransaction,
)


def create_transaction():

    return WalletTransaction(
        sender="address-1",
        inputs=[
            TransactionInput(
                source_address="address-1",
                amount=100,
            )
        ],
        outputs=[
            TransactionOutput(
                destination_address="address-2",
                amount=90,
            )
        ],
        timestamp=100,
    )


def test_transaction_creation():

    transaction = create_transaction()

    assert (
        transaction.sender
        == "address-1"
    )

    assert (
        transaction.transaction_id
    )


def test_transaction_id_determinism():

    first = create_transaction()

    second = create_transaction()

    assert (
        first.transaction_id
        == second.transaction_id
    )


def test_attach_signature():

    transaction = create_transaction()

    transaction.attach_signature(
        "signature"
    )

    assert (
        transaction.signature
        == "signature"
    )


def test_transaction_serialization():

    transaction = create_transaction()

    data = transaction.to_dict()

    assert (
        data["sender"]
        == "address-1"
    )

    assert (
        data["transaction_id"]
        == transaction.transaction_id
    )