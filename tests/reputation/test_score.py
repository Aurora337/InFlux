from influx.reputation.validator_score import (
    ValidatorScore,
)


def test_score_creation():

    score = ValidatorScore(
        validator_id="node-1",
    )

    assert (
        score.validator_id
        == "node-1"
    )

    assert (
        score.score
        == 100
    )


def test_record_success():

    score = ValidatorScore(
        validator_id="node-1",
    )

    score.record_success()

    assert (
        score.successful_actions
        == 1
    )

    assert (
        score.score
        == 101
    )


def test_record_failure():

    score = ValidatorScore(
        validator_id="node-1",
    )

    score.record_failure()

    assert (
        score.failed_actions
        == 1
    )

    assert (
        score.score
        == 99
    )


def test_score_never_negative():

    score = ValidatorScore(
        validator_id="node-1",
        score=0,
    )

    score.record_failure()

    assert (
        score.score
        == 0
    )


def test_health_check():

    healthy = ValidatorScore(
        validator_id="node-1",
        score=10,
    )

    unhealthy = ValidatorScore(
        validator_id="node-2",
        score=0,
    )

    assert healthy.healthy()

    assert (
        unhealthy.healthy()
        is False
    )