from influx.network.cluster.cluster import Cluster
from influx.network.cluster.cluster_config import ClusterConfig
from influx.network.cluster.cluster_manager import ClusterManager
from influx.network.cluster.cluster_member import ClusterMember
from influx.network.cluster.cluster_registry import ClusterRegistry
from influx.network.cluster.cluster_validator import ClusterValidator


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


def create_manager() -> ClusterManager:
    return ClusterManager(
        registry=ClusterRegistry(),
        validator=ClusterValidator(),
    )


def test_register_cluster() -> None:
    manager = create_manager()

    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    assert manager.register(cluster)

    assert manager.count() == 1


def test_add_member() -> None:
    manager = create_manager()

    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    manager.register(cluster)

    assert manager.add_member(
        "cluster-1",
        create_member("node-2"),
    )

    assert manager.count() == 1


def test_remove_member() -> None:
    manager = create_manager()

    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    manager.register(cluster)

    assert manager.remove_member(
        "cluster-1",
        "node-1",
    ) is False


def test_unregister_cluster() -> None:
    manager = create_manager()

    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    manager.register(cluster)

    manager.unregister("cluster-1")

    assert manager.count() == 0