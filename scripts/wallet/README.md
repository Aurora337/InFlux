# Wallet Key Rotation CLI

This directory contains tooling for rotating wallet keys and resigning persisted wallet transactions.

## Script

- `rotate_and_resign.py`: rotate an account key in the wallet keystore and optionally re-sign transaction JSON files.

## Usage

Run a single account rotation and resign transactions:

```bash
python scripts/wallet/rotate_and_resign.py \
  --storage .wallet \
  --account acct-cli \
  --private-hex <private_hex> \
  --public-hex <public_hex> \
  --created-at 1234567890 \
  --resign-dir storage/txs \
  --backup
```

Use dry-run mode to preview changes without writing:

```bash
python scripts/wallet/rotate_and_resign.py --storage .wallet --account acct-cli --private-hex <private_hex> --public-hex <public_hex> --dry-run --resign-dir storage/txs
```

Use a batch file to process multiple account rotations:

```bash
python scripts/wallet/rotate_and_resign.py --storage .wallet --batch-file batch.jsonl --backup
```

Or use the wrapper script for a consistent environment:

```bash
scripts/wallet/run.sh --storage .wallet --account acct-cli --private-hex <private_hex> --public-hex <public_hex> --resign-dir storage/txs --backup
```

If the package is installed in the current environment, you can also invoke the entrypoint directly:

```bash
influx-wallet-rotate --storage .wallet --account acct-cli --private-hex <private_hex> --public-hex <public_hex> --resign-dir storage/txs --backup
```

Batch file format is newline-delimited JSON with fields:

```json
{ "account": "acct-cli", "private_hex": "...", "public_hex": "...", "created_at": 1234567890, "resign_dir": "storage/txs", "resign_extension": "json", "resign_backup": true }
```
