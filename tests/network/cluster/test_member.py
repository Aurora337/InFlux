from influx.network.cluster.cluster_member import (
    ClusterMember,
)


def create_member():

    return ClusterMember(
        node_id="node-1",
        address="127.0.0.1",
        port=9000,
    )


def test_member_defaults():

    member = create_member()

    assert member.node_id == "node-1"
    assert member.active
    assert not member.validator


def test_activate():

    member = create_member()

    member.deactivate()

    assert not member.active

    member.activate()

    assert member.active


def test_deactivate():

    member = create_member()

    member.deactivate()

    assert not member.active


def test_member_roles():

    member = ClusterMember(
        node_id="node-1",
        address="127.0.0.1",
        port=9000,
        validator=True,
        storage=True,
        archive=True,
    )

    assert member.validator
    assert member.storage
    assert member.archive


def test_snapshot():

    member = create_member()

    snapshot = member.snapshot()

    assert snapshot["node_id"] == "node-1"
    assert snapshot["port"] == 9000