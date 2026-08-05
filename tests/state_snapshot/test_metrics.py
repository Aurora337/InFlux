from influx.state_snapshot.snapshot_metrics import (
    SnapshotMetrics,
)


def test_snapshot_metrics():

    metrics = SnapshotMetrics()

    metrics.record_snapshot()

    metrics.record_checkpoint()

    metrics.record_load()

    metrics.record_bootstrap(
        True
    )

    metrics.record_bootstrap(
        False
    )

    assert (
        metrics.snapshots_created
        == 1
    )

    assert (
        metrics.checkpoints_created
        == 1
    )

    assert (
        metrics.snapshots_loaded
        == 1
    )

    assert (
        metrics.bootstrap_successes
        == 1
    )

    assert (
        metrics.bootstrap_failures
        == 1
    )


def test_metrics_snapshot():

    metrics = SnapshotMetrics()

    result = metrics.snapshot()

    assert (
        "snapshots_created"
        in result
    )

    assert (
        "bootstrap_successes"
        in result
    )