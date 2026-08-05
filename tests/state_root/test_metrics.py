from influx.state_root.state_root_metrics import (
    StateRootMetrics,
)


def test_root_record():

    metrics = StateRootMetrics()

    metrics.record_root()

    assert (
        metrics.roots_generated
        == 1
    )


def test_commitment_record():

    metrics = StateRootMetrics()

    metrics.record_commitment()

    assert (
        metrics.commitments_created
        == 1
    )


def test_validation_success():

    metrics = StateRootMetrics()

    metrics.record_validation(
        True
    )

    assert (
        metrics.validations_performed
        == 1
    )

    assert (
        metrics.validation_failures
        == 0
    )


def test_validation_failure():

    metrics = StateRootMetrics()

    metrics.record_validation(
        False
    )

    assert (
        metrics.validation_failures
        == 1
    )


def test_comparison_record():

    metrics = StateRootMetrics()

    metrics.record_comparison()

    assert (
        metrics.root_comparisons
        == 1
    )


def test_snapshot():

    metrics = StateRootMetrics()

    snapshot = metrics.snapshot()

    assert (
        "roots_generated"
        in snapshot
    )

    assert (
        "validation_failures"
        in snapshot
    )