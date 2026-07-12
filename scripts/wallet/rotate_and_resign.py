#!/usr/bin/env python3
"""CLI tool to rotate an account key and optionally re-sign JSON transactions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from influx.wallet.manager import WalletManager
from influx.wallet.signing import Ed25519WalletSigner


def resign_transactions_in_dir(directory: Path, public_hex: str, private_hex: str) -> int:
    signer = Ed25519WalletSigner()
    count = 0
    for path in directory.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Expect transaction-like object with sender and transaction_id
        if not isinstance(data, dict):
            continue
        if "sender" in data and "transaction_id" in data:
            # create a minimal transaction wrapper to sign
            from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput

            tx = WalletTransaction(
                sender=data["sender"],
                inputs=[TransactionInput(**item) for item in data.get("inputs", [])],
                outputs=[TransactionOutput(**item) for item in data.get("outputs", [])],
                timestamp=data.get("timestamp", 0),
            )
            sig = signer.sign(tx, private_hex)
            data["signature"] = sig
            path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
            count += 1
    return count


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rotate account key and optionally resign transactions")
    parser.add_argument("--storage", default=".wallet", help="wallet storage directory")
    parser.add_argument("--account", required=True, help="account id")
    parser.add_argument("--private-hex", required=True, help="private key hex to add as new version")
    parser.add_argument("--public-hex", required=True, help="public key hex corresponding to private key")
    parser.add_argument("--created-at", type=int, default=0)
    parser.add_argument("--resign-dir", help="directory containing JSON transactions to resign")

    args = parser.parse_args(argv)

    mgr = WalletManager(Path(args.storage))
    entry = mgr.add_key_for_account(args.account, args.private_hex, args.public_hex, args.created_at)
    print(f"Added key version {entry.version} for account {args.account}")

    if args.resign_dir:
        d = Path(args.resign_dir)
        if not d.exists():
            print("Resign directory does not exist")
            return 2
        count = resign_transactions_in_dir(d, args.public_hex, args.private_hex)
        print(f"Re-signed {count} transactions in {d}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
