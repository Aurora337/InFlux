from influx.wallet.signing import (
    WalletSigner,
)

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


def test_transaction_signing():

    signer = WalletSigner()

    transaction = create_transaction()

    signature = signer.sign(
        transaction,
        "private-key",
    )

    assert signature

    assert (
        transaction.signature
        == signature
    )


def test_signature_verification():

    signer = WalletSigner()

    transaction = create_transaction()

    signer.sign(
        transaction,
        "private-key",
    )

    assert (
        signer.verify(
            transaction,
            "private-key",
        )
        is True
    )


def test_invalid_signature_verification():

    signer = WalletSigner()

    transaction = create_transaction()

    signer.sign(
        transaction,
        "private-key",
    )

    assert (
        signer.verify(
            transaction,
            "wrong-key",
        )
        is False
    )


def test_unsigned_transaction_fails():

    signer = WalletSigner()

    transaction = create_transaction()

    assert (
        signer.verify(
            transaction,
            "private-key",
        )
        is False
    )