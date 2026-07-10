from influx.identity.identity import (
    Identity,
)


def test_identity_creation():

    identity = Identity(
        identity_id="node-1",
        public_key="pub-key",
        created_at=100,
    )

    assert (
        identity.identity_id
        == "node-1"
    )

    assert (
        identity.public_key
        == "pub-key"
    )

    assert (
        identity.active
        is True
    )


def test_identity_deactivate():

    identity = Identity(
        identity_id="node-1",
        public_key="pub-key",
        created_at=100,
    )

    identity.deactivate()

    assert (
        identity.active
        is False
    )


def test_identity_activate():

    identity = Identity(
        identity_id="node-1",
        public_key="pub-key",
        created_at=100,
        active=False,
    )

    identity.activate()

    assert (
        identity.active
        is True
    )


def test_identity_serialization():

    identity = Identity(
        identity_id="node-1",
        public_key="pub-key",
        created_at=100,
    )

    data = identity.to_dict()

    assert (
        data["identity_id"]
        == "node-1"
    )

    assert (
        data["public_key"]
        == "pub-key"
    )