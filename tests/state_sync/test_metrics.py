from influx.state_sync.sync_metrics import (
    SyncMetrics,
)


def test_attempt():

    metrics = SyncMetrics()

    metrics.record_attempt()

    assert (
        metrics.sync_attempts
        == 1
    )


def test_success():

    metrics = SyncMetrics()

    metrics.record_success()

    assert (
        metrics.successful_syncs
        == 1
    )


def test_failure():

    metrics = SyncMetrics()

    metrics.record_failure()

    assert (
        metrics.failed_syncs
        == 1
    )


def test_diff_tracking():

    metrics = SyncMetrics()

    metrics.record_diff()

    assert (
        metrics.diffs_generated
        == 1
    )


def test_proof_tracking():

    metrics = SyncMetrics()

    metrics.record_proof()

    metrics.record_verification()

    assert (
        metrics.proofs_created
        == 1
    )

    assert (
        metrics.proofs_verified
        == 1
    )


def test_snapshot():

    metrics = SyncMetrics()

    snapshot = metrics.snapshot()

    assert (
        "sync_attempts"
        in snapshot
    )

    assert (
        "proofs_verified"
        in snapshot
    )