from pathlib import Path
from tempfile import TemporaryDirectory

from influx.wallet.manager import WalletManager
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput
from nacl.signing import SigningKey
import json

from influx.wallet.cli import main as rotate_main


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
        tx_path.write_text(json.dumps(tx.to_dict()), encoding="utf-8")

        # generate key
        sk = SigningKey.generate()
        sk_hex = sk.encode().hex()
        pk_hex = sk.verify_key.encode().hex()

        # call CLI main in dry-run mode (should not write signature)
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
            "--dry-run",
        ])
        assert rv == 0

        content = tx_path.read_text(encoding="utf-8")
        # dry-run should not add an ed25519 signature
        assert "ed25519:" not in content

        # now run for real and verify signature added
        rv2 = rotate_main([
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
        assert rv2 == 0

        content2 = tx_path.read_text(encoding="utf-8")
        # real run should add an ed25519 signature
        assert "ed25519:" in content2
