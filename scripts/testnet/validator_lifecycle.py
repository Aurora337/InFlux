#!/usr/bin/env python3
"""Deterministic validator lifecycle state machine."""

from __future__ import annotations

import argparse
from enum import Enum
import json


class LifecycleError(RuntimeError):
    """Raised when lifecycle transitions are attempted out of order."""


class ValidatorState(str, Enum):
    CREATED = "CREATED"
    REGISTERED = "REGISTERED"
    STARTED = "STARTED"
    HEALTHY = "HEALTHY"
    STOPPED = "STOPPED"
    RECOVERED = "RECOVERED"


class ValidatorLifecycle:
    def __init__(self, validator_id: str) -> None:
        self.validator_id = validator_id
        self.state: ValidatorState | None = None
        self.registered = False
        self.started = False
        self.healthy = False
        self.recoverable = False

    def _require_state(self, expected: ValidatorState, action: str) -> None:
        if self.state != expected:
            current = self.state.value if self.state else "UNINITIALIZED"
            raise LifecycleError(f"cannot {action} from {current}; expected {expected.value}")

    def create_validator(self) -> None:
        if self.state is not None:
            raise LifecycleError("validator has already been created")
        self.state = ValidatorState.CREATED

    def register_validator(self) -> None:
        self._require_state(ValidatorState.CREATED, "register")
        self.registered = True
        self.state = ValidatorState.REGISTERED

    def start_validator(self) -> None:
        self._require_state(ValidatorState.REGISTERED, "start")
        self.state = ValidatorState.STARTED
        self.started = True
        self.healthy = True
        self.state = ValidatorState.HEALTHY

    def stop_validator(self) -> None:
        self._require_state(ValidatorState.HEALTHY, "stop")
        self.state = ValidatorState.STOPPED
        self.started = False
        self.healthy = False
        self.recoverable = True

    def recover_validator(self) -> None:
        self._require_state(ValidatorState.STOPPED, "recover")
        self.started = True
        self.healthy = True
        self.state = ValidatorState.RECOVERED

    def emit_status(self) -> dict:
        if self.state is None:
            raise LifecycleError("validator must be created before status emission")
        return {
            "validator_id": self.validator_id,
            "state": self.state.value,
            "registered": self.registered,
            "started": self.started,
            "healthy": self.healthy,
            "recoverable": self.recoverable,
        }

    def run_full_lifecycle(self) -> dict:
        self.create_validator()
        self.register_validator()
        self.start_validator()
        self.stop_validator()
        self.recover_validator()
        return self.emit_status()


def run_validator_lifecycle(validator_id: str = "validator-1") -> dict:
    lifecycle = ValidatorLifecycle(validator_id=validator_id)
    return lifecycle.run_full_lifecycle()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic validator lifecycle state machine")
    parser.add_argument("--validator-id", default="validator-1", help="Validator identifier")
    parser.add_argument("--output-json", default="", help="Optional output path for JSON artifact")
    args = parser.parse_args()

    result = run_validator_lifecycle(validator_id=args.validator_id)

    payload = json.dumps(result, indent=2, sort_keys=True)

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    print(payload)


if __name__ == "__main__":
    main()
