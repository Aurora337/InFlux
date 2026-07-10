from influx.reputation.reputation_metrics import (
    ReputationMetrics,
)


def test_reputation_metrics():

    metrics = ReputationMetrics()

    metrics.record_fault()

    metrics.record_penalty()

    metrics.record_recovery_start()

    metrics.record_recovery_complete()

    metrics.record_score_update()

    assert (
        metrics.faults_detected
        == 1
    )

    assert (
        metrics.penalties_applied
        == 1
    )

    assert (
        metrics.recoveries_started
        == 1
    )

    assert (
        metrics.recoveries_completed
        == 1
    )

    assert (
        metrics.score_updates
        == 1
    )


def test_metrics_snapshot():

    metrics = ReputationMetrics()

    snapshot = metrics.snapshot()

    assert (
        "faults_detected"
        in snapshot
    )

    assert (
        "penalties_applied"
        in snapshot
    )

    assert (
        "recoveries_completed"
        in snapshot
    )