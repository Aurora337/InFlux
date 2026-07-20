from influx.network.transport.transport_metrics import (
    TransportMetrics,
)


def test_record_send():

    metrics = TransportMetrics()

    metrics.record_send()

    snapshot = metrics.snapshot()

    assert snapshot["messages_sent"] == 1


def test_record_receive():

    metrics = TransportMetrics()

    metrics.record_receive()

    snapshot = metrics.snapshot()

    assert snapshot["messages_received"] == 1


def test_record_failure():

    metrics = TransportMetrics()

    metrics.record_failure()

    snapshot = metrics.snapshot()

    assert snapshot["failures"] == 1


def test_snapshot():

    metrics = TransportMetrics()

    snapshot = metrics.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )