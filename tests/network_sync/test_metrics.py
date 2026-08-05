from influx.network_sync.network_metrics import (
    NetworkMetrics,
)


def test_network_metrics():

    metrics = NetworkMetrics()

    metrics.record_fork()
    metrics.record_resolution()

    metrics.record_selection()

    metrics.record_sync(True)
    metrics.record_sync(False)

    assert metrics.forks_detected == 1
    assert metrics.forks_resolved == 1
    assert metrics.chain_selections == 1

    assert metrics.sync_requests == 2
    assert metrics.sync_successes == 1
    assert metrics.sync_failures == 1


def test_metrics_snapshot():

    metrics = NetworkMetrics()

    snapshot = metrics.snapshot()

    assert "forks_detected" in snapshot
    assert "forks_resolved" in snapshot
    assert "sync_requests" in snapshot
    assert "chain_selections" in snapshot