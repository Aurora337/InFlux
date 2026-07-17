from influx.network.node.node_metrics import NodeMetrics


def test_metrics_defaults() -> None:
    metrics = NodeMetrics()

    assert metrics.messages_sent == 0
    assert metrics.messages_received == 0
    assert metrics.peers_connected == 0
    assert metrics.errors == 0
    assert metrics.uptime_seconds == 0


def test_metrics_update() -> None:
    metrics = NodeMetrics()

    metrics.record_send()
    metrics.record_receive()
    metrics.peer_connected()
    metrics.synchronized()
    metrics.record_error()
    metrics.tick()

    assert metrics.messages_sent == 1
    assert metrics.messages_received == 1
    assert metrics.peers_connected == 1
    assert metrics.synchronization_events == 1
    assert metrics.errors == 1
    assert metrics.uptime_seconds == 1


def test_peer_disconnect() -> None:
    metrics = NodeMetrics()

    metrics.peer_connected()
    metrics.peer_connected()

    assert metrics.peers_connected == 2

    metrics.peer_disconnected()

    assert metrics.peers_connected == 1