from influx.operations.metrics import OperationsMetrics


def test_metrics_snapshot() -> None:
    metrics = OperationsMetrics()

    metrics.nodes_online = 4
    metrics.validators_active = 2

    metrics.record_event()
    metrics.record_message()

    snapshot = metrics.snapshot()

    assert snapshot["nodes_online"] == 4
    assert snapshot["validators_active"] == 2
    assert snapshot["events_recorded"] == 1
    assert snapshot["messages_processed"] == 1