from influx.network.gossip.gossip_metrics import (
    GossipMetrics,
)


def test_received():

    metrics = GossipMetrics()

    metrics.record_received()

    assert metrics.messages_received == 1


def test_propagated():

    metrics = GossipMetrics()

    metrics.record_propagated()

    assert metrics.messages_propagated == 1


def test_rejected():

    metrics = GossipMetrics()

    metrics.record_rejected()

    assert metrics.messages_rejected == 1


def test_duplicate():

    metrics = GossipMetrics()

    metrics.record_duplicate()

    assert metrics.duplicates_detected == 1


def test_expired():

    metrics = GossipMetrics()

    metrics.record_expired()

    assert metrics.expired_messages == 1


def test_snapshot():

    metrics = GossipMetrics()

    snapshot = metrics.snapshot()

    assert "messages_received" in snapshot
    assert "messages_propagated" in snapshot