#!/usr/bin/env python3
"""Deterministic validator lifecycle state machine."""

from __future__ import annotations

import argparse
import json


class LifecycleError(RuntimeError):
    """Raised when lifecycle transitions are attempted out of order."""


class ValidatorLifecycle:
    def __init__(self, validator_id: str) -> None:
        self.validator_id = validator_id
        self.created = False
        self.registered = False
        self.started = False
        self.healthy = False
        self.shutdown_complete = False
        self.recoverable = False

    def create(self) -> None:
        self.created = True

    def register(self) -> None:
        if not self.created:
            raise LifecycleError("validator must be created before registration")
        self.registered = True

    def start(self) -> None:
        if not self.registered:
            raise LifecycleError("validator must be registered before startup")
        self.started = True
        self.healthy = True

    def shutdown(self) -> None:
        if not self.started:
            raise LifecycleError("validator must be started before shutdown")
        self.shutdown_complete = True
        self.healthy = False

    def recover(self) -> None:
        if not self.shutdown_complete:
            raise LifecycleError("validator must be shut down before recovery")
        self.recoverable = True
        self.started = True
        self.healthy = True

    def run_full_lifecycle(self) -> dict:
        self.create()
        self.register()
        self.start()
        self.shutdown()
        self.recover()

        return {
            "validator_id": self.validator_id,
            "registered": self.registered,
            "started": self.started,
            "healthy": self.healthy,
            "recoverable": self.recoverable,
        }


def run_validator_lifecycle(validator_id: str = "validator-1") -> dict:
    lifecycle = ValidatorLifecycle(validator_id=validator_id)
    return lifecycle.run_full_lifecycle()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic validator lifecycle state machine")
    parser.add_argument("--validator-id", default="validator-1", help="Validator identifier")
    parser.add_argument("--output-json", default="", help="Optional output path for JSON artifact")
    args = parser.parse_args()

    result = run_validator_lifecycle(validator_id=args.validator_id)

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
