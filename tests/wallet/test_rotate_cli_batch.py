from pathlib import Path
from tempfile import TemporaryDirectory

from influx.wallet.manager import WalletManager
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput
from nacl.signing import SigningKey
import json

from influx.wallet.cli import main as rotate_main


def test_batch_rotate_and_resign_cli():
    with TemporaryDirectory() as td:
        base = Path(td)
        mgr = WalletManager(base)
        mgr.create_account("acct-batch", "id-batch", 1)

        tx_dir = base / "txs"
        tx_dir.mkdir()
        tx = WalletTransaction(
            sender="acct-batch",
            inputs=[TransactionInput(source_address="acct-batch", amount=1)],
            outputs=[TransactionOutput(destination_address="dst", amount=1)],
            timestamp=1,
        )
        tx_path = tx_dir / "tx1.json"
        tx_path.write_text(json.dumps(tx.to_dict()), encoding="utf-8")

        sk = SigningKey.generate()
        sk_hex = sk.encode().hex()
        pk_hex = sk.verify_key.encode().hex()

        batch_file = base / "batch.jsonl"
        batch_file.write_text(json.dumps({
            "account": "acct-batch",
            "private_hex": sk_hex,
            "public_hex": pk_hex,
            "created_at": 2,
            "resign_dir": str(tx_dir),
            "resign_pattern": "*.json",
            "resign_backup": True,
        }), encoding="utf-8")

        rv = rotate_main([
            "--storage",
            str(base),
            "--batch-file",
            str(batch_file),
            "--backup",
        ])
        assert rv == 0
        assert (tx_dir / "tx1.json.bak").exists()
        assert "ed25519:" in tx_path.read_text(encoding="utf-8")
