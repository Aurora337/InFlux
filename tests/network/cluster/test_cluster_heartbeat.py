from influx.network.cluster.cluster_heartbeat import ClusterHeartbeat


def test_defaults():
    heartbeat = ClusterHeartbeat()

    assert heartbeat.heartbeat_count == 0


def test_beat():
    heartbeat = ClusterHeartbeat()

    heartbeat.beat()

    assert heartbeat.heartbeat_count == 1


def test_snapshot():
    heartbeat = ClusterHeartbeat()

    assert "heartbeat_count" in heartbeat.snapshot()