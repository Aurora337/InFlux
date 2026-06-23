import json

import pytest

from scripts.testnet.validator_lifecycle import (
    LifecycleError,
    ValidatorLifecycle,
    run_validator_lifecycle,
)


def test_create_validator() -> None:
    lifecycle = ValidatorLifecycle("validator-1")
    lifecycle.create_validator()
    assert lifecycle.emit_status() == {
        "validator_id": "validator-1",
        "state": "CREATED",
        "registered": False,
        "started": False,
        "healthy": False,
        "recoverable": False,
    }


def test_register_validator() -> None:
    lifecycle = ValidatorLifecycle("validator-1")
    lifecycle.create_validator()
    lifecycle.register_validator()
    assert lifecycle.emit_status()["state"] == "REGISTERED"
    assert lifecycle.emit_status()["registered"] is True


def test_start_validator() -> None:
    lifecycle = ValidatorLifecycle("validator-1")
    lifecycle.create_validator()
    lifecycle.register_validator()
    lifecycle.start_validator()
    assert lifecycle.emit_status() == {
        "validator_id": "validator-1",
        "state": "HEALTHY",
        "registered": True,
        "started": True,
        "healthy": True,
        "recoverable": False,
    }


def test_stop_validator() -> None:
    lifecycle = ValidatorLifecycle("validator-1")
    lifecycle.create_validator()
    lifecycle.register_validator()
    lifecycle.start_validator()
    lifecycle.stop_validator()
    assert lifecycle.emit_status() == {
        "validator_id": "validator-1",
        "state": "STOPPED",
        "registered": True,
        "started": False,
        "healthy": False,
        "recoverable": True,
    }


def test_recover_validator() -> None:
    lifecycle = ValidatorLifecycle("validator-1")
    lifecycle.create_validator()
    lifecycle.register_validator()
    lifecycle.start_validator()
    lifecycle.stop_validator()
    lifecycle.recover_validator()
    assert lifecycle.emit_status() == {
        "validator_id": "validator-1",
        "state": "RECOVERED",
        "registered": True,
        "started": True,
        "healthy": True,
        "recoverable": True,
    }


def test_invalid_transition_rejected() -> None:
    lifecycle = ValidatorLifecycle("validator-1")
    with pytest.raises(LifecycleError):
        lifecycle.start_validator()

    lifecycle.create_validator()
    lifecycle.register_validator()
    lifecycle.start_validator()
    with pytest.raises(LifecycleError):
        lifecycle.recover_validator()


def test_deterministic_output() -> None:
    first = run_validator_lifecycle(validator_id="validator-1")
    second = run_validator_lifecycle(validator_id="validator-1")
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
