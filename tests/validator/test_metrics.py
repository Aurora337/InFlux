from influx.validator.validator_metrics import (
    ValidatorMetrics,
)


def test_validator_metrics():

    metrics = ValidatorMetrics()

    metrics.record_registration()

    metrics.record_activation()

    metrics.record_deactivation()

    metrics.record_schedule()

    metrics.record_rotation()

    assert (
        metrics.validators_registered
        == 1
    )

    assert (
        metrics.activations
        == 1
    )

    assert (
        metrics.deactivations
        == 1
    )

    assert (
        metrics.schedules_created
        == 1
    )

    assert (
        metrics.rotations_created
        == 1
    )


def test_metrics_snapshot():

    metrics = ValidatorMetrics()

    snapshot = metrics.snapshot()

    assert (
        "validators_registered"
        in snapshot
    )

    assert (
        "schedules_created"
        in snapshot
    )

    assert (
        "rotations_created"
        in snapshot
    )