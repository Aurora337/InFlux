from influx.replication.replication_metrics import (
    ReplicationMetrics,
)


def test_record_created():

    metrics = ReplicationMetrics()

    metrics.record_created()

    assert metrics.sessions_created == 1


def test_record_completed():

    metrics = ReplicationMetrics()

    metrics.record_completed()

    assert metrics.sessions_completed == 1


def test_record_failed():

    metrics = ReplicationMetrics()

    metrics.record_failed()

    assert metrics.sessions_failed == 1


def test_record_cancelled():

    metrics = ReplicationMetrics()

    metrics.record_cancelled()

    assert metrics.sessions_cancelled == 1


def test_record_bytes():

    metrics = ReplicationMetrics()

    metrics.record_bytes(2048)

    assert metrics.bytes_replicated == 2048


def test_record_diff():

    metrics = ReplicationMetrics()

    metrics.record_diff()

    assert metrics.state_diffs == 1


def test_record_verification_failure():

    metrics = ReplicationMetrics()

    metrics.record_verification_failure()

    assert metrics.verification_failures == 1


def test_average_sync_time():

    metrics = ReplicationMetrics()

    metrics.update_average_sync_time(
        10.0
    )

    metrics.update_average_sync_time(
        20.0
    )

    assert metrics.average_sync_time == 15.0


def test_snapshot():

    metrics = ReplicationMetrics()

    snapshot = metrics.snapshot()

    assert "sessions_created" in snapshot
    assert "average_sync_time" in snapshot