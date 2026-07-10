from influx.reputation.penalty_engine import (
    PenaltyEngine,
    PenaltyResult,
)


def test_apply_penalty():

    engine = PenaltyEngine()

    result = engine.apply(
        validator_id="node-1",
        severity=5,
    )

    assert isinstance(
        result,
        PenaltyResult,
    )

    assert (
        result.validator_id
        == "node-1"
    )

    assert (
        result.penalty
        == 5
    )


def test_high_penalty_disables_validator():

    engine = PenaltyEngine()

    result = engine.apply(
        validator_id="node-1",
        severity=10,
    )

    assert (
        result.active
        is False
    )


def test_negative_penalty_protection():

    engine = PenaltyEngine()

    result = engine.apply(
        validator_id="node-1",
        severity=-5,
    )

    assert (
        result.penalty
        == 0
    )