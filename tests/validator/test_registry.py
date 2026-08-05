from influx.validator.validator import (
    Validator,
)

from influx.validator.validator_registry import (
    ValidatorRegistry,
)


def test_register_validator():

    registry = ValidatorRegistry()

    validator = Validator(
        validator_id="node-1",
        stake=100,
    )

    registry.register(
        validator
    )

    result = registry.get(
        "node-1"
    )

    assert result is not None

    assert (
        result.validator_id
        == "node-1"
    )


def test_missing_validator():

    registry = ValidatorRegistry()

    assert (
        registry.get(
            "missing"
        )
        is None
    )


def test_active_validators():

    registry = ValidatorRegistry()

    registry.register(
        Validator(
            "node-b",
            100,
        )
    )

    registry.register(
        Validator(
            "node-a",
            100,
        )
    )

    registry.register(
        Validator(
            "inactive",
            100,
            False,
        )
    )

    validators = (
        registry.active_validators()
    )

    assert [
        validator.validator_id
        for validator in validators
    ] == [
        "node-a",
        "node-b",
    ]


def test_registry_count():

    registry = ValidatorRegistry()

    registry.register(
        Validator(
            "node-1",
            100,
        )
    )

    assert (
        registry.count()
        == 1
    )