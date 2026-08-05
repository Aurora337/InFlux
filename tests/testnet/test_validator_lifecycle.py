import json
import subprocess

from scripts.testnet.validator_lifecycle import ValidatorLifecycle, run_validator_lifecycle


def test_validator_lifecycle_default_output() -> None:
    result = run_validator_lifecycle()
    assert result == {
        "validator_id": "validator-1",
        "registered": True,
        "started": True,
        "healthy": True,
        "recoverable": True,
    }


def test_validator_lifecycle_cli_output() -> None:
    run = subprocess.run(
        ["python", "scripts/testnet/validator_lifecycle.py"],
        cwd="/workspaces/InFlux",
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr
    payload = json.loads(run.stdout)
    assert payload["validator_id"] == "validator-1"
    assert payload["registered"] is True
    assert payload["started"] is True
    assert payload["healthy"] is True
    assert payload["recoverable"] is True


def test_validator_lifecycle_is_deterministic() -> None:
    first = run_validator_lifecycle()
    second = run_validator_lifecycle()
    assert first == second


def test_validator_lifecycle_requires_creation_before_registration() -> None:
    lifecycle = ValidatorLifecycle("validator-x")
    try:
        lifecycle.register()
        raise AssertionError("registration should fail before create")
    except RuntimeError:
        pass
