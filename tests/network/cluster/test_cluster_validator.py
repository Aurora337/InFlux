from influx.network.cluster.cluster import Cluster
from influx.network.cluster.cluster_config import ClusterConfig
from influx.network.cluster.cluster_member import ClusterMember
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


def test_validate_cluster() -> None:
    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    validator = ClusterValidator()

    assert validator.validate(cluster)


def test_duplicate_member_fails() -> None:
    cluster = create_cluster()

    cluster.add_member(
        create_member("node-1")
    )

    cluster.add_member(
        create_member("node-1")
    )

    validator = ClusterValidator()

    assert not validator.validate(cluster)