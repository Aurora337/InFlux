from influx.network.sync.sync_metrics import SyncMetrics


def test_metrics():

    metrics = SyncMetrics()

    metrics.record_snapshot()
    metrics.record_message()
    metrics.record_failure()

    snapshot = metrics.snapshot()

    assert snapshot["snapshots"] == 1
    assert snapshot["messages"] == 1
    assert snapshot["failures"] == 1