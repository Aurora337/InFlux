import pytest

from influx.node_runtime.identity import NodeIdentity
from influx.node_runtime.errors import NodeIdentityError


def test_valid_identity() -> None:
    identity = NodeIdentity(
        node_id="node-1",
        public_key="key",
    )

    identity.validate()


def test_missing_identity_values() -> None:
    identity = NodeIdentity(
        node_id="",
        public_key="",
    )

    with pytest.raises(NodeIdentityError):
        identity.validate()