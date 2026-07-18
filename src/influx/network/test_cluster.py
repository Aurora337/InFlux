from influx.network.cluster.cluster import Cluster
from influx.network.cluster.cluster_config import ClusterConfig
from influx.network.cluster.cluster_member import ClusterMember


def create_cluster() -> Cluster:
    return Cluster(
        cluster_id="cluster-1",
        config=ClusterConfig(),
    )


def create_member(node_id: str) -> ClusterMember:
    return ClusterMember(
        node_id=node_id,
        address="127.0.0.1",
        port=9000,
    )


def test_add_member() -> None:
    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    assert cluster.member_count() == 1


def test_remove_member() -> None:
    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    cluster.remove_member("node-1")

    assert cluster.member_count() == 0


def test_state_updates() -> None:
    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    assert cluster.state.member_count == 1