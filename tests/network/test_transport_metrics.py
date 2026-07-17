from influx.network.transport.transport_metrics import TransportMetrics


def test_metrics_defaults() -> None:
    metrics = TransportMetrics()

    assert metrics.sessions_opened == 0
    assert metrics.sessions_closed == 0
    assert metrics.send_operations == 0
    assert metrics.receive_operations == 0
    assert metrics.bytes_sent == 0
    assert metrics.bytes_received == 0
    assert metrics.failures == 0
    assert metrics.heartbeat_failures == 0


def test_metrics_update() -> None:
    metrics = TransportMetrics()

    metrics.record_open()
    metrics.record_send(128)
    metrics.record_receive(256)
    metrics.record_close()

    assert metrics.sessions_opened == 1
    assert metrics.sessions_closed == 1
    assert metrics.send_operations == 1
    assert metrics.receive_operations == 1
    assert metrics.bytes_sent == 128
    assert metrics.bytes_received == 256