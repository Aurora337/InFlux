from influx.network.synchronization.sync_metrics import (
    SyncMetrics,
)


def test_request_metric():

    metrics = SyncMetrics()

    metrics.record_request()

    assert metrics.requests_received == 1


def test_request_complete():

    metrics = SyncMetrics()

    metrics.record_request_complete()

    assert metrics.requests_completed == 1


def test_response_sent():

    metrics = SyncMetrics()

    metrics.record_response_sent()

    assert metrics.responses_sent == 1


def test_response_received():

    metrics = SyncMetrics()

    metrics.record_response_received()

    assert metrics.responses_received == 1


def test_validation_failure():

    metrics = SyncMetrics()

    metrics.record_validation_failure()

    assert metrics.validation_failures == 1


def test_failed_sync():

    metrics = SyncMetrics()

    metrics.record_failure()

    assert metrics.failed_syncs == 1


def test_snapshot():

    metrics = SyncMetrics()

    snapshot = metrics.snapshot()

    assert "requests_received" in snapshot
    assert "failed_syncs" in snapshot