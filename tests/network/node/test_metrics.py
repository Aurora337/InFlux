from influx.network.node.node_metrics import NodeMetrics


def test_record_sent():

    metrics = NodeMetrics()

    metrics.record_sent()

    assert metrics.messages_sent == 1


def test_record_received():

    metrics = NodeMetrics()

    metrics.record_received()

    assert metrics.messages_received == 1


def test_record_peer():

    metrics = NodeMetrics()

    metrics.record_peer(5)

    assert metrics.peers_connected == 5


def test_record_sync():

    metrics = NodeMetrics()

    metrics.record_sync()

    assert metrics.synchronization_events == 1


def test_failure():

    metrics = NodeMetrics()

    metrics.record_failure()

    assert metrics.failures == 1


def test_snapshot():

    metrics = NodeMetrics()

    snapshot = metrics.snapshot()

    assert "messages_sent" in snapshot
    assert "failures" in snapshot