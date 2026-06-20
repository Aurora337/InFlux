#!/usr/bin/env python3
"""Build a bootstrap peer registry from validator configs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def bootstrap(validators_dir: Path, output_path: Path) -> dict:
    peers = []
    for path in sorted(validators_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        peers.append(
            {
                "name": payload["name"],
                "endpoint": f"{payload['host']}:{payload['port']}",
            }
        )

    network = {
        "peer_count": len(peers),
        "peers": peers,
        "bootstrap_status": "ready" if peers else "empty",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(network, indent=2) + "\n", encoding="utf-8")
    return network


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap testnet peer registry")
    parser.add_argument(
        "--validators-dir",
        default="testnet/validators",
        help="Directory containing validator configs",
    )
    parser.add_argument(
        "--output",
        default="testnet/bootstrap/network.json",
        help="Path to write network bootstrap JSON",
    )
    args = parser.parse_args()

    network = bootstrap(Path(args.validators_dir), Path(args.output))
    print(f"Bootstrapped network: {args.output}")
    print(f"Peers discovered: {network['peer_count']}")


if __name__ == "__main__":
    main()
