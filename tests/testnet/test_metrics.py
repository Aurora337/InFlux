from influx.testnet.metrics import (
    NetworkMetrics,
)


def test_metrics_creation() -> None:
    metrics = NetworkMetrics(
        node_count=10,
        online_nodes=8,
        events_processed=100,
    )

    assert metrics.node_count == 10
    assert metrics.online_nodes == 8
    assert metrics.events_processed == 100


def test_availability_ratio() -> None:
    metrics = NetworkMetrics(
        node_count=10,
        online_nodes=8,
        events_processed=100,
    )

    assert metrics.availability_ratio() == 0.8


def test_zero_nodes() -> None:
    metrics = NetworkMetrics(
        node_count=0,
        online_nodes=0,
        events_processed=0,
    )

    assert metrics.availability_ratio() == 0.0