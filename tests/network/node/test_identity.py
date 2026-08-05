from influx.network.node.node_identity import NodeIdentity


def test_identity_defaults():

    identity = NodeIdentity()

    assert identity.node_id is not None
    assert identity.role == "validator"


def test_set_metadata():

    identity = NodeIdentity()

    identity.set_metadata(
        "region",
        "test",
    )

    assert identity.metadata["region"] == "test"


def test_snapshot():

    identity = NodeIdentity(
        public_key="key123",
        role="archive",
    )

    snapshot = identity.snapshot()

    assert snapshot["public_key"] == "key123"
    assert snapshot["role"] == "archive"