#!/usr/bin/env python3
"""CLI tool to rotate an account key and optionally re-sign JSON transactions."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from influx.wallet.manager import WalletManager
from influx.wallet.signing import Ed25519WalletSigner
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput


logger = logging.getLogger("rotate_and_resign")


def resign_transactions_in_dir(directory: Path, private_hex: str, dry_run: bool = False) -> int:
    signer = Ed25519WalletSigner()
    count = 0
    for path in directory.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if "sender" in data and "transaction_id" in data:
            tx = WalletTransaction(
                sender=data["sender"],
                inputs=[TransactionInput(**item) for item in data.get("inputs", [])],
                outputs=[TransactionOutput(**item) for item in data.get("outputs", [])],
                timestamp=data.get("timestamp", 0),
            )
            sig = signer.sign(tx, private_hex)
            if dry_run:
                logger.info("dry-run: would sign %s", path)
            else:
                data["signature"] = sig
                path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
                logger.info("signed %s", path)
            count += 1
    return count


def process_batch_file(batch_file: Path, mgr: WalletManager, dry_run: bool = False) -> int:
    count = 0
    for line in batch_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except Exception:
            logger.warning("skipping invalid line in batch file: %s", line)
            continue
        acct = item.get("account")
        priv = item.get("private_hex")
        pub = item.get("public_hex")
        created_at = int(item.get("created_at", 0))
        resign_dir = item.get("resign_dir")
        if not acct or not priv or not pub:
            logger.warning("batch item missing required fields: %s", item)
            continue
        if not dry_run:
            mgr.add_key_for_account(acct, priv, pub, created_at)
            logger.info("added key for %s", acct)
        else:
            logger.info("dry-run: would add key for %s", acct)
        if resign_dir:
            d = Path(resign_dir)
            if d.exists():
                resign_transactions_in_dir(d, priv, dry_run=dry_run)
        count += 1
    return count


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rotate account key and optionally resign JSON transactions")
    parser.add_argument("--storage", default=".wallet", help="wallet storage directory")
    parser.add_argument("--account", help="account id (required unless --batch-file provided)")
    parser.add_argument("--private-hex", help="private key hex to add as new version")
    parser.add_argument("--public-hex", help="public key hex corresponding to private key")
    parser.add_argument("--created-at", type=int, default=0)
    parser.add_argument("--resign-dir", help="directory containing JSON transactions to resign")
    parser.add_argument("--batch-file", help="newline-delimited JSON file with batch operations")
    parser.add_argument("--dry-run", action="store_true", help="do not write changes, just report")
    parser.add_argument("--log-file", help="path to write logs")

    args = parser.parse_args(argv)

    # configure logging
    handlers = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file))
    logging.basicConfig(level=logging.INFO, handlers=handlers)

    mgr = WalletManager(Path(args.storage))

    total = 0
    if args.batch_file:
        bf = Path(args.batch_file)
        if not bf.exists():
            logger.error("batch file does not exist: %s", bf)
            return 2
        total = process_batch_file(bf, mgr, dry_run=args.dry_run)
        logger.info("processed %d batch entries", total)
        return 0

    if not args.account or not args.private_hex or not args.public_hex:
        logger.error("--account, --private-hex, and --public-hex are required when not using --batch-file")
        return 2

    if not args.dry_run:
        entry = mgr.add_key_for_account(args.account, args.private_hex, args.public_hex, args.created_at)
        logger.info("Added key version %d for account %s", entry.version, args.account)
    else:
        logger.info("dry-run: would add key for %s", args.account)

    if args.resign_dir:
        d = Path(args.resign_dir)
        if not d.exists():
            logger.error("Resign directory does not exist: %s", d)
            return 2
        count = resign_transactions_in_dir(d, args.private_hex, dry_run=args.dry_run)
        logger.info("processed resign for %d transactions in %s", count, d)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
