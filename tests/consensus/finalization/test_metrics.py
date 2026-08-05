from influx.consensus.finalization.finality_metrics import (
    FinalityMetrics,
)


def test_certificate_record():

    metrics = FinalityMetrics()

    metrics.record_certificate()

    assert (
        metrics.certificates_created
        == 1
    )


def test_finalization_record():

    metrics = FinalityMetrics()

    metrics.record_finalization()

    assert (
        metrics.blocks_finalized
        == 1
    )


def test_quorum_failure():

    metrics = FinalityMetrics()

    metrics.record_quorum_failure()

    assert (
        metrics.quorum_failures
        == 1
    )


def test_validation_failure():

    metrics = FinalityMetrics()

    metrics.record_validation_failure()

    assert (
        metrics.validation_failures
        == 1
    )


def test_finalization_time():

    metrics = FinalityMetrics()

    metrics.update_finalization_time(
        10
    )

    metrics.update_finalization_time(
        20
    )

    assert (
        metrics.average_finalization_time
        == 15
    )


def test_snapshot():

    metrics = FinalityMetrics()

    snapshot = metrics.snapshot()

    assert (
        "blocks_finalized"
        in snapshot
    )

    assert (
        "average_finalization_time"
        in snapshot
    )