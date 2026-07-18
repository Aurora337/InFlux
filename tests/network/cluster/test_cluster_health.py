from influx.network.cluster.cluster_health import ClusterHealth


def test_defaults():
    health = ClusterHealth()

    assert health.healthy()


def test_snapshot():
    health = ClusterHealth()

    snapshot = health.snapshot()

    assert snapshot["healthy"]