from influx.network.network_metrics import NetworkMetrics


def test_peer_metrics():

    metrics = NetworkMetrics()

    metrics.record_peer_connected()
    metrics.record_peer_disconnected()

    assert metrics.peers_connected == 1
    assert metrics.peers_disconnected == 1


def test_message_metrics():

    metrics = NetworkMetrics()

    metrics.record_route()
    metrics.record_drop()

    assert metrics.messages_routed == 1
    assert metrics.messages_dropped == 1


def test_sync_metrics():

    metrics = NetworkMetrics()

    metrics.record_sync()
    metrics.record_replication()

    assert metrics.sync_rounds == 1
    assert metrics.replication_rounds == 1


def test_snapshot():

    metrics = NetworkMetrics()

    metrics.record_route()

    snapshot = metrics.snapshot()

    assert snapshot["messages_routed"] == 1