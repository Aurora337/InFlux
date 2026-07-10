from influx.network.cluster.cluster import (
    Cluster,
)

from influx.network.cluster.cluster_member import (
    ClusterMember,
)

from influx.network.cluster.leader_election import (
    LeaderElection,
)


def create_member(
    node_id,
):

    return ClusterMember(
        node_id=node_id,
        address="127.0.0.1",
        port=9000,
    )


def test_elect_leader():

    cluster = Cluster(
        cluster_id="cluster-1",
    )

    cluster.add_member(
        create_member("node-b")
    )

    cluster.add_member(
        create_member("node-a")
    )

    election = LeaderElection()

    leader = election.elect(
        cluster
    )

    assert leader is not None
    assert leader.node_id == "node-a"


def test_no_leader_empty_cluster():

    cluster = Cluster(
        cluster_id="cluster-1",
    )

    election = LeaderElection()

    leader = election.elect(
        cluster
    )

    assert leader is None


def test_inactive_member_not_selected():

    cluster = Cluster(
        cluster_id="cluster-1",
    )

    member = create_member(
        "node-a"
    )

    member.deactivate()

    cluster.add_member(
        member
    )

    election = LeaderElection()

    leader = election.elect(
        cluster
    )

    assert leader is None


def test_leader_snapshot():

    cluster = Cluster(
        cluster_id="cluster-1",
    )

    cluster.add_member(
        create_member("node-a")
    )

    leader = LeaderElection().elect(
        cluster
    )

    snapshot = leader.snapshot()

    assert snapshot["node_id"] == "node-a"