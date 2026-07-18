from influx.network.cluster.cluster_topology import ClusterTopology


def test_connect():
    topology = ClusterTopology()

    topology.connect("A", "B")

    assert "B" in topology.neighbors("A")
    assert "A" in topology.neighbors("B")


def test_disconnect():
    topology = ClusterTopology()

    topology.connect("A", "B")
    topology.disconnect("A", "B")

    assert topology.neighbors("A") == set()


def test_snapshot():
    topology = ClusterTopology()

    topology.connect("A", "B")

    assert "A" in topology.snapshot()