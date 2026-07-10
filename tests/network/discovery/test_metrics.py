from influx.network.discovery.discovery_metrics import (
    DiscoveryMetrics,
)


def test_record_attempt():

    metrics = DiscoveryMetrics()

    metrics.record_attempt()

    assert metrics.discovery_attempts == 1


def test_record_discovered():

    metrics = DiscoveryMetrics()

    metrics.record_discovered()

    assert metrics.peers_discovered == 1


def test_record_rejected():

    metrics = DiscoveryMetrics()

    metrics.record_rejected()

    assert metrics.peers_rejected == 1


def test_record_removed():

    metrics = DiscoveryMetrics()

    metrics.record_removed()

    assert metrics.peers_removed == 1


def test_validation_failure():

    metrics = DiscoveryMetrics()

    metrics.record_validation_failure()

    assert metrics.validation_failures == 1


def test_snapshot():

    metrics = DiscoveryMetrics()

    snapshot = metrics.snapshot()

    assert "peers_discovered" in snapshot