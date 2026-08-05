from influx.network.cluster.cluster_discovery import ClusterDiscovery
from influx.network.cluster.cluster_member import ClusterMember


def create_member() -> ClusterMember:
    return ClusterMember(
        node_id="node-1",
        address="127.0.0.1",
        port=9000,
    )


def test_discover():
    discovery = ClusterDiscovery()

    assert discovery.discover(create_member())


def test_duplicate_discover():
    discovery = ClusterDiscovery()

    member = create_member()

    discovery.discover(member)

    assert not discovery.discover(member)


def test_lookup():
    discovery = ClusterDiscovery()

    member = create_member()

    discovery.discover(member)

    assert discovery.get("node-1") is member


def test_clear():
    discovery = ClusterDiscovery()

    discovery.discover(create_member())

    discovery.clear()

    assert discovery.members() == []