from __future__ import annotations

import argparse
import json
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Iterable, Optional

from influx.wallet.manager import WalletManager
from influx.wallet.signing import Ed25519WalletSigner
from influx.wallet.transactions import WalletTransaction, TransactionInput, TransactionOutput

logger = logging.getLogger("influx.wallet.cli")


def gather_transaction_files(directory: Path, pattern: str = "*.json") -> Iterable[Path]:
    pattern_value = pattern if "*" in pattern else f"*.{pattern.lstrip('.')}"
    yield from directory.rglob(pattern_value)


def safe_write_json(path: Path, data: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent)) as tmp:
        json.dump(data, tmp, indent=2, sort_keys=True)
        tmp.flush()
        temp_path = Path(tmp.name)
    shutil.move(str(temp_path), str(path))


def resign_transactions_in_dir(
    directory: Path,
    private_hex: str,
    dry_run: bool = False,
    backup: bool = False,
    pattern: str = "*.json",
) -> int:
    signer = Ed25519WalletSigner()
    count = 0
    for path in gather_transaction_files(directory, pattern=pattern):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Skipping unreadable or invalid JSON file: %s", path)
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
                if backup:
                    backup_path = path.with_suffix(path.suffix + ".bak")
                    shutil.copy2(path, backup_path)
                    logger.info("created backup %s", backup_path)
                data["signature"] = sig
                safe_write_json(path, data)
                logger.info("signed %s", path)
            count += 1
    return count


def process_batch_file(
    batch_file: Path,
    mgr: WalletManager,
    dry_run: bool = False,
    backup: bool = False,
    pattern: str = "*.json",
) -> int:
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
        resign_pattern = item.get("resign_pattern", pattern)
        resign_backup = item.get("resign_backup", backup)
        if not acct or not priv or not pub:
            logger.warning("batch item missing required fields: %s", item)
            continue
        if dry_run:
            logger.info("dry-run: would add key for %s", acct)
        else:
            mgr.add_key_for_account(acct, priv, pub, created_at)
            logger.info("added key for %s", acct)
        if resign_dir:
            d = Path(resign_dir)
            if d.exists():
                resign_transactions_in_dir(
                    d,
                    priv,
                    dry_run=dry_run,
                    backup=resign_backup,
                    pattern=resign_pattern,
                )
        count += 1
    return count


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rotate account key and optionally resign persisted wallet transactions")
    parser.add_argument("--storage", default=".wallet", help="wallet storage directory")
    parser.add_argument("--account", help="account id (required unless --batch-file provided)")
    parser.add_argument("--private-hex", help="private key hex to add as new version")
    parser.add_argument("--public-hex", help="public key hex corresponding to private key")
    parser.add_argument("--created-at", type=int, default=0)
    parser.add_argument("--resign-dir", help="directory containing transaction files to resign")
    parser.add_argument("--resign-extension", "--resign-pattern", default="*.json", help="file extension or glob pattern for transaction files")
    parser.add_argument("--backup", action="store_true", help="create backup files before modifying transactions")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="logging level")
    parser.add_argument("--batch-file", help="newline-delimited JSON file with batch operations")
    parser.add_argument("--dry-run", action="store_true", help="do not write changes, just report")
    parser.add_argument("--log-file", help="path to write logs")

    args = parser.parse_args(argv)

    handlers: list[logging.Handler] = []
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file))
    logging.basicConfig(level=getattr(logging, args.log_level), handlers=handlers)

    mgr = WalletManager(Path(args.storage))

    if args.batch_file:
        bf = Path(args.batch_file)
        if not bf.exists():
            logger.error("batch file does not exist: %s", bf)
            return 2
        total = process_batch_file(
            bf,
            mgr,
            dry_run=args.dry_run,
            backup=args.backup,
            pattern=args.resign_extension,
        )
        logger.info("processed %d batch entries", total)
        return 0

    if not args.account or not args.private_hex or not args.public_hex:
        logger.error("--account, --private-hex, and --public-hex are required when not using --batch-file")
        return 2

    if args.dry_run:
        logger.info("dry-run: would add key for %s", args.account)
    else:
        entry = mgr.add_key_for_account(args.account, args.private_hex, args.public_hex, args.created_at)
        logger.info("Added key version %d for account %s", entry.version, args.account)

    if args.resign_dir:
        d = Path(args.resign_dir)
        if not d.exists():
            logger.error("Resign directory does not exist: %s", d)
            return 2
        count = resign_transactions_in_dir(
            d,
            args.private_hex,
            dry_run=args.dry_run,
            backup=args.backup,
            pattern=args.resign_extension,
        )
        logger.info("processed resign for %d transactions in %s", count, d)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
