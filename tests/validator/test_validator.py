from influx.validator.validator import (
    Validator,
)


def test_validator_creation():

    validator = Validator(
        validator_id="node-1",
        stake=100,
    )

    assert (
        validator.validator_id
        == "node-1"
    )

    assert (
        validator.stake
        == 100
    )

    assert validator.active is True


def test_validator_eligibility():

    validator = Validator(
        validator_id="node-1",
        stake=100,
    )

    assert validator.eligible()


def test_zero_stake_not_eligible():

    validator = Validator(
        validator_id="node-1",
        stake=0,
    )

    assert (
        validator.eligible()
        is False
    )


def test_deactivate_validator():

    validator = Validator(
        validator_id="node-1",
        stake=100,
    )

    validator.deactivate()

    assert (
        validator.active
        is False
    )

    assert (
        validator.eligible()
        is False
    )


def test_activate_validator():

    validator = Validator(
        validator_id="node-1",
        stake=100,
    )

    validator.deactivate()

    validator.activate()

    assert validator.active