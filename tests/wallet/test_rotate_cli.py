from pathlib import Path
from tempfile import TemporaryDirectory

from influx.wallet.manager import WalletManager
from influx.wallet.signing import Ed25519WalletSigner
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput
from nacl.signing import SigningKey

from scripts.wallet.rotate_and_resign import main as rotate_main


def test_rotate_and_resign_cli():
    with TemporaryDirectory() as td:
        base = Path(td)
        mgr = WalletManager(base)
        acct = mgr.create_account("acct-cli", "id-cli", 1)

        # create a sample transaction JSON to be resigned
        resign_dir = base / "txs"
        resign_dir.mkdir()
        tx = WalletTransaction(
            sender="acct-cli",
            inputs=[TransactionInput(source_address="acct-cli", amount=1)],
            outputs=[TransactionOutput(destination_address="dst", amount=1)],
            timestamp=1,
        )
        tx_path = resign_dir / "tx1.json"
        tx_path.write_text(tx.to_dict().__str__(), encoding="utf-8")

        # generate key
        sk = SigningKey.generate()
        sk_hex = sk.encode().hex()
        pk_hex = sk.verify_key.encode().hex()

        # call CLI main
        rv = rotate_main([
            "--storage",
            str(base),
            "--account",
            "acct-cli",
            "--private-hex",
            sk_hex,
            "--public-hex",
            pk_hex,
            "--created-at",
            "2",
            "--resign-dir",
            str(resign_dir),
        ])
        assert rv == 0

        # verify tx file updated with signature
        content = tx_path.read_text(encoding="utf-8")
        assert "signature" in content
