from influx.network.connection.connection_metrics import ConnectionMetrics


def test_metrics_open():

    metrics = ConnectionMetrics()

    metrics.record_open()

    assert metrics.connections_opened == 1
    assert metrics.active_connections == 1


def test_average_latency():

    metrics = ConnectionMetrics()

    metrics.record_latency(10)
    metrics.record_latency(20)

    assert metrics.average_latency == 15