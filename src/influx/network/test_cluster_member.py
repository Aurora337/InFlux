from influx.network.cluster.cluster_member import ClusterMember


def create_member() -> ClusterMember:
    return ClusterMember(
        node_id="node-1",
        address="127.0.0.1",
        port=9000,
    )


def test_activate_deactivate() -> None:
    member = create_member()

    member.deactivate()
    assert not member.active

    member.activate()
    assert member.active


def test_snapshot() -> None:
    member = create_member()

    snapshot = member.snapshot()

    assert snapshot["node_id"] == "node-1"
    assert snapshot["address"] == "127.0.0.1"
    assert snapshot["port"] == 9000


def test_validate() -> None:
    member = create_member()

    member.validate()