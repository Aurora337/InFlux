#!/usr/bin/env python3
"""Create validator configuration files for testnet bootstrapping."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def create_validator(name: str, host: str, port: int, output_dir: Path) -> Path:
    payload = {
        "name": name,
        "host": host,
        "port": port,
        "status": "created",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name}.json"
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a validator config")
    parser.add_argument("--name", required=True, help="Validator name")
    parser.add_argument("--host", default="127.0.0.1", help="Validator host")
    parser.add_argument("--port", type=int, default=9100, help="Validator port")
    parser.add_argument(
        "--output-dir",
        default="testnet/validators",
        help="Directory for validator configs",
    )
    args = parser.parse_args()

    path = create_validator(args.name, args.host, args.port, Path(args.output_dir))
    print(f"Created validator config: {path}")


if __name__ == "__main__":
    main()
