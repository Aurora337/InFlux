from influx.wallet.keystore import KeyStore
from influx.wallet.signing import Ed25519WalletSigner
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput
from nacl.signing import SigningKey


def create_transaction():
    return WalletTransaction(
        sender="address-1",
        inputs=[TransactionInput(source_address="address-1", amount=100)],
        outputs=[TransactionOutput(destination_address="address-2", amount=90)],
        timestamp=100,
    )


def test_key_rotation_keeps_old_signatures():
    ks = KeyStore()
    # initial key
    sk1 = SigningKey.generate()
    sk1_hex = sk1.encode().hex()
    vk1_hex = sk1.verify_key.encode().hex()
    entry1 = ks.add_key("acct-1", sk1_hex, vk1_hex, 1)

    signer = Ed25519WalletSigner()
    tx = create_transaction()
    sig1 = signer.sign(tx, sk1_hex)
    assert signer.verify(tx, vk1_hex)

    # rotate
    sk2 = SigningKey.generate()
    sk2_hex = sk2.encode().hex()
    vk2_hex = sk2.verify_key.encode().hex()
    entry2 = ks.rotate_key("acct-1", sk2_hex, vk2_hex, 2)

    # active key should be new
    active = ks.get_active_key("acct-1")
    assert active.version == entry2.version
    # old signature still verifies with old public key
    assert signer.verify(tx, vk1_hex)

    # new signature with new key verifies
    tx2 = create_transaction()
    sig2 = signer.sign(tx2, sk2_hex)
    assert signer.verify(tx2, vk2_hex)
