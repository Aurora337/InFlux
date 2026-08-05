from influx.network.cluster.cluster_quorum import ClusterQuorum


def test_quorum_defaults():
    quorum = ClusterQuorum()

    assert not quorum.reached()


def test_quorum_reached():
    quorum = ClusterQuorum(required=3)

    quorum.present = 3

    assert quorum.reached()


def test_snapshot():
    quorum = ClusterQuorum()

    assert "required" in quorum.snapshot()