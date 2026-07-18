from influx.network.cluster.cluster_monitor import ClusterMonitor


def test_counters():
    monitor = ClusterMonitor()

    monitor.observe()
    monitor.warning()
    monitor.error()

    assert monitor.observations == 1
    assert monitor.warnings == 1
    assert monitor.errors == 1


def test_snapshot():
    monitor = ClusterMonitor()

    assert "observations" in monitor.snapshot()