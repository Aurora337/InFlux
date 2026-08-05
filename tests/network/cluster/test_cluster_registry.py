from influx.network.cluster.cluster import Cluster
from influx.network.cluster.cluster_config import ClusterConfig
from influx.network.cluster.cluster_registry import ClusterRegistry


def create_cluster() -> Cluster:
    return Cluster(
        cluster_id="cluster-1",
        config=ClusterConfig(),
    )


def test_register_cluster() -> None:
    registry = ClusterRegistry()

    cluster = create_cluster()

    registry.register(cluster)

    assert registry.count() == 1
    assert registry.exists("cluster-1")


def test_get_cluster() -> None:
    registry = ClusterRegistry()

    cluster = create_cluster()

    registry.register(cluster)

    assert registry.get("cluster-1") is cluster


def test_unregister_cluster() -> None:
    registry = ClusterRegistry()

    registry.register(create_cluster())

    registry.unregister("cluster-1")

    assert registry.count() == 0


def test_clear_registry() -> None:
    registry = ClusterRegistry()

    registry.register(create_cluster())

    registry.clear()

    assert registry.count() == 0