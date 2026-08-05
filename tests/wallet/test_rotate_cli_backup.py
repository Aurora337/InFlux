from pathlib import Path
from tempfile import TemporaryDirectory

from influx.wallet.manager import WalletManager
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput
from nacl.signing import SigningKey
import json

from scripts.wallet.rotate_and_resign import main as rotate_main


def test_rotate_and_resign_cli_with_backup_and_pattern():
    with TemporaryDirectory() as td:
        base = Path(td)
        mgr = WalletManager(base)
        mgr.create_account("acct-cli", "id-cli", 1)

        resign_dir = base / "txs"
        resign_dir.mkdir()
        tx1 = WalletTransaction(
            sender="acct-cli",
            inputs=[TransactionInput(source_address="acct-cli", amount=1)],
            outputs=[TransactionOutput(destination_address="dst", amount=1)],
            timestamp=1,
        )
        tx1_path = resign_dir / "tx1.wallet.json"
        tx1_path.write_text(json.dumps(tx1.to_dict()), encoding="utf-8")

        sk = SigningKey.generate()
        sk_hex = sk.encode().hex()
        pk_hex = sk.verify_key.encode().hex()

        rv = rotate_main([
            "--storage",
            str(base),
            "--account",
            "acct-cli",
            "--private-hex",
            sk_hex,
            "--public-hex",
            pk_hex,
            "--resign-dir",
            str(resign_dir),
            "--resign-extension",
            "*.wallet.json",
            "--backup",
        ])
        assert rv == 0
        assert (resign_dir / "tx1.wallet.json.bak").exists()
        content = tx1_path.read_text(encoding="utf-8")
        assert "ed25519:" in content
