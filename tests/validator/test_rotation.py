from influx.validator.validator import (
    Validator,
)

from influx.validator.validator_rotation import (
    ValidatorRotation,
    RotationRound,
)


def test_create_rotation():

    rotation = ValidatorRotation()

    validators = [
        Validator(
            "node-a",
            100,
        )
    ]

    result = rotation.create_round(
        1,
        validators,
    )

    assert isinstance(
        result,
        RotationRound,
    )

    assert (
        result.round_id
        == 1
    )


def test_get_rotation():

    rotation = ValidatorRotation()

    rotation.create_round(
        5,
        [],
    )

    result = rotation.get_round(
        5
    )

    assert result is not None

    assert (
        result.round_id
        == 5
    )


def test_rotation_order():

    rotation = ValidatorRotation()

    rotation.create_round(
        3,
        [],
    )

    rotation.create_round(
        1,
        [],
    )

    rotation.create_round(
        2,
        [],
    )

    assert (
        rotation.rounds()
        ==
        [1, 2, 3]
    )