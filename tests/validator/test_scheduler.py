from influx.validator.validator import (
    Validator,
)

from influx.validator.validator_registry import (
    ValidatorRegistry,
)

from influx.validator.validator_scheduler import (
    ValidatorScheduler,
)


def test_select_validator():

    registry = ValidatorRegistry()

    registry.register(
        Validator(
            "node-a",
            100,
        )
    )

    registry.register(
        Validator(
            "node-b",
            100,
        )
    )

    scheduler = ValidatorScheduler(
        registry
    )

    selected = scheduler.select(
        0
    )

    assert selected is not None

    assert (
        selected.validator_id
        == "node-a"
    )


def test_schedule_creation():

    registry = ValidatorRegistry()

    registry.register(
        Validator(
            "node-a",
            100,
        )
    )

    registry.register(
        Validator(
            "node-b",
            100,
        )
    )

    scheduler = ValidatorScheduler(
        registry
    )

    schedule = scheduler.schedule(
        4
    )

    assert [
        validator.validator_id
        for validator in schedule
    ] == [
        "node-a",
        "node-b",
        "node-a",
        "node-b",
    ]


def test_empty_schedule():

    registry = ValidatorRegistry()

    scheduler = ValidatorScheduler(
        registry
    )

    assert (
        scheduler.schedule(5)
        == []
    )