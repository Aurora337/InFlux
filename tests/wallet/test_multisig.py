from nacl.signing import SigningKey
from influx.wallet.multisig import MultisigSigner, MultisigPolicy
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput


def create_transaction():
    return WalletTransaction(
        sender="addr",
        inputs=[TransactionInput(source_address="addr", amount=1)],
        outputs=[TransactionOutput(destination_address="dst", amount=1)],
        timestamp=1,
    )


def test_multisig_threshold_pass():
    sk1 = SigningKey.generate()
    sk2 = SigningKey.generate()
    sk3 = SigningKey.generate()

    pk1 = sk1.verify_key.encode().hex()
    pk2 = sk2.verify_key.encode().hex()
    pk3 = sk3.verify_key.encode().hex()

    private_keys = [sk1.encode().hex(), sk2.encode().hex(), sk3.encode().hex()]
    public_keys = [pk1, pk2, pk3]

    policy = MultisigPolicy(signers=[pk1, pk2, pk3], threshold=2)

    signer = MultisigSigner()
    tx = create_transaction()
    # sign with first two
    blob = signer.sign(tx, private_keys_hex=private_keys[:2], public_keys_hex=public_keys[:2])
    tx.attach_signature(blob)

    assert signer.verify(tx, policy) is True


def test_multisig_threshold_fail():
    sk1 = SigningKey.generate()
    sk2 = SigningKey.generate()
    pk1 = sk1.verify_key.encode().hex()
    pk2 = sk2.verify_key.encode().hex()

    private_keys = [sk1.encode().hex()]
    public_keys = [pk1]

    policy = MultisigPolicy(signers=[pk1, pk2], threshold=2)

    signer = MultisigSigner()
    tx = create_transaction()
    blob = signer.sign(tx, private_keys_hex=private_keys, public_keys_hex=public_keys)
    tx.attach_signature(blob)

    assert signer.verify(tx, policy) is False
