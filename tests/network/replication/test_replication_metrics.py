from influx.network.replication.replication_metrics import (
    ReplicationMetrics,
)


def test_defaults():
    metrics = ReplicationMetrics()

    assert metrics.tasks_started == 0


def test_snapshot():
    metrics = ReplicationMetrics()

    assert "tasks_completed" in metrics.snapshot()