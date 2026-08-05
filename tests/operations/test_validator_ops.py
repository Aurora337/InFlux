from influx.operations.validator_ops import (
    ValidatorOperations,
    ValidatorStatus,
)


def test_add_validator() -> None:
    operations = ValidatorOperations()

    operations.update(
        ValidatorStatus(
            validator_id="validator-1",
            online=True,
            participating=True,
            healthy=True,
        )
    )

    assert operations.validator_count() == 1
    assert operations.healthy_count() == 1


def test_readiness() -> None:
    operations = ValidatorOperations()

    operations.update(
        ValidatorStatus(
            validator_id="validator-1",
            online=True,
            participating=True,
            healthy=True,
        )
    )

    operations.update(
        ValidatorStatus(
            validator_id="validator-2",
            online=True,
            participating=True,
            healthy=False,
        )
    )

    assert operations.readiness() == 0.5


def test_empty_readiness() -> None:
    operations = ValidatorOperations()

    assert operations.readiness() == 0.0