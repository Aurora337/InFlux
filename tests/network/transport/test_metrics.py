from influx.network.transport.transport_metrics import TransportMetrics


def test_record_open():

    metrics = TransportMetrics()

    metrics.record_open()

    assert metrics.sessions_opened == 1


def test_record_close():

    metrics = TransportMetrics()

    metrics.record_close()

    assert metrics.sessions_closed == 1


def test_record_send():

    metrics = TransportMetrics()

    metrics.record_send(100)

    assert metrics.send_operations == 1
    assert metrics.bytes_sent == 100


def test_record_receive():

    metrics = TransportMetrics()

    metrics.record_receive(200)

    assert metrics.receive_operations == 1
    assert metrics.bytes_received == 200


def test_failure():

    metrics = TransportMetrics()

    metrics.record_failure()

    assert metrics.failures == 1


def test_heartbeat_failure():

    metrics = TransportMetrics()

    metrics.record_heartbeat_failure()

    assert metrics.heartbeat_failures == 1


def test_latency():

    metrics = TransportMetrics()

    metrics.record_latency(10)

    metrics.record_latency(20)

    assert metrics.average_latency == 15


def test_snapshot():

    metrics = TransportMetrics()

    snapshot = metrics.snapshot()

    assert "bytes_sent" in snapshot
    assert "average_latency" in snapshot