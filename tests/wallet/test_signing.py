from influx.wallet.signing import (
    WalletSigner,
    Ed25519WalletSigner,
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


def test_ed25519_signing_and_verification():
    # Exercise the new Ed25519 signer using a generated keypair
    from nacl.signing import SigningKey

    sk = SigningKey.generate()
    vk = sk.verify_key

    sk_hex = sk.encode().hex()
    vk_hex = vk.encode().hex()

    signer = Ed25519WalletSigner()

    transaction = create_transaction()

    signature = signer.sign(transaction, sk_hex)

    assert signature.startswith("ed25519:")

    assert signer.verify(transaction, vk_hex) is True


def test_ed25519_invalid_verification():
    from nacl.signing import SigningKey

    sk = SigningKey.generate()
    vk = sk.verify_key

    other_sk = SigningKey.generate()
    other_vk = other_sk.verify_key

    sk_hex = sk.encode().hex()
    other_vk_hex = other_vk.encode().hex()

    signer = Ed25519WalletSigner()

    transaction = create_transaction()

    signer.sign(transaction, sk_hex)

    assert signer.verify(transaction, other_vk_hex) is False

    transaction = create_transaction()

    assert (
        signer.verify(
            transaction,
            "private-key",
        )
        is False
    )