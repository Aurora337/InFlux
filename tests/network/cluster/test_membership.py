from influx.network.cluster.cluster import (
    Cluster,
)

from influx.network.cluster.cluster_member import (
    ClusterMember,
)

from influx.network.cluster.membership import (
    Membership,
)

from influx.network.cluster.membership_policy import (
    MembershipPolicy,
)


def create_cluster():

    return Cluster(
        cluster_id="cluster-1",
    )


def create_member(
    node_id="node-1",
):

    return ClusterMember(
        node_id=node_id,
        address="127.0.0.1",
        port=9000,
    )


def test_join_member():

    membership = Membership()

    cluster = create_cluster()

    result = membership.join(
        cluster,
        create_member(),
    )

    assert result
    assert cluster.member_count() == 1


def test_duplicate_join():

    membership = Membership()

    cluster = create_cluster()

    member = create_member()

    membership.join(
        cluster,
        member,
    )

    result = membership.join(
        cluster,
        member,
    )

    assert not result


def test_leave_member():

    membership = Membership()

    cluster = create_cluster()

    member = create_member()

    membership.join(
        cluster,
        member,
    )

    result = membership.leave(
        cluster,
        "node-1",
    )

    assert result
    assert cluster.member_count() == 0


def test_capacity_limit():

    policy = MembershipPolicy(
        max_members=1,
    )

    membership = Membership(
        policy
    )

    cluster = create_cluster()

    assert membership.join(
        cluster,
        create_member("node-1"),
    )

    result = membership.join(
        cluster,
        create_member("node-2"),
    )

    assert not result


def test_validator_requirement():

    policy = MembershipPolicy(
        require_validator=True,
    )

    membership = Membership(
        policy
    )

    cluster = create_cluster()

    member = create_member()

    result = membership.join(
        cluster,
        member,
    )

    assert not result