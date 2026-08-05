from influx.network.cluster.cluster import (
    Cluster,
)

from influx.network.cluster.cluster_member import (
    ClusterMember,
)

from influx.network.cluster.cluster_state import (
    ClusterState,
)


def create_cluster():

    return Cluster(
        cluster_id="cluster-1",
    )


def create_member():

    return ClusterMember(
        node_id="node-1",
        address="127.0.0.1",
        port=9000,
    )


def test_cluster_defaults():

    cluster = create_cluster()

    assert cluster.cluster_id == "cluster-1"

    assert (
        cluster.state
        == ClusterState.INITIALIZING
    )


def test_form():

    cluster = create_cluster()

    cluster.form()

    assert (
        cluster.state
        == ClusterState.FORMING
    )


def test_activate():

    cluster = create_cluster()

    cluster.activate()

    assert (
        cluster.state
        == ClusterState.ACTIVE
    )


def test_add_member():

    cluster = create_cluster()

    result = cluster.add_member(
        create_member()
    )

    assert result
    assert cluster.member_count() == 1


def test_duplicate_member():

    cluster = create_cluster()

    member = create_member()

    cluster.add_member(member)

    result = cluster.add_member(
        member
    )

    assert not result


def test_lookup_member():

    cluster = create_cluster()

    member = create_member()

    cluster.add_member(
        member
    )

    found = cluster.lookup(
        "node-1"
    )

    assert found is member


def test_remove_member():

    cluster = create_cluster()

    member = create_member()

    cluster.add_member(
        member
    )

    result = cluster.remove_member(
        "node-1"
    )

    assert result
    assert cluster.member_count() == 0


def test_snapshot():

    cluster = create_cluster()

    snapshot = cluster.snapshot()

    assert snapshot["cluster_id"] == "cluster-1"
    assert "state" in snapshot