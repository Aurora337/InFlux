#!/usr/bin/env python3
"""Simulate launching a validator node from configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def launch_validator(config_path: Path) -> dict:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["status"] = "running"
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch a validator from config")
    parser.add_argument("--config", required=True, help="Path to validator JSON config")
    args = parser.parse_args()

    status = launch_validator(Path(args.config))
    print(f"{status['validator_id']} connected")


if __name__ == "__main__":
    main()
