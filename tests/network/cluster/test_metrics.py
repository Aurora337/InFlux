from influx.network.cluster.cluster_metrics import (
    ClusterMetrics,
)


def test_join_metric():

    metrics = ClusterMetrics()

    metrics.record_join()

    assert metrics.joins == 1


def test_leave_metric():

    metrics = ClusterMetrics()

    metrics.record_leave()

    assert metrics.leaves == 1


def test_election_metric():

    metrics = ClusterMetrics()

    metrics.record_election()

    assert metrics.elections == 1


def test_failure_metric():

    metrics = ClusterMetrics()

    metrics.record_failure()

    assert metrics.failures == 1


def test_snapshot():

    metrics = ClusterMetrics()

    snapshot = metrics.snapshot()

    assert "joins" in snapshot
    assert "elections" in snapshot
    assert "failures" in snapshot