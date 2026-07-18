from influx.network.cluster.cluster_sync import ClusterSync


def test_defaults():
    sync = ClusterSync()

    assert sync.synchronized()


def test_snapshot():
    sync = ClusterSync()

    snapshot = sync.snapshot()

    assert snapshot["synchronized"]