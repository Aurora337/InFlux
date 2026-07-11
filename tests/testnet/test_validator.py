import pytest

from influx.testnet.validator import (
    ValidatorManager,
)

from influx.testnet.node import (
    TestnetNode,
)

from influx.testnet.exceptions import (
    NodeError,
)


def test_validator_activation() -> None:
    node = TestnetNode(
        node_id="validator-1",
        validator=True,
    )

    manager = ValidatorManager()

    state = manager.activate(node)

    assert state.active is True
    assert state.node_id == "validator-1"


def test_non_validator_rejected() -> None:
    node = TestnetNode(
        node_id="node-1",
        validator=False,
    )

    manager = ValidatorManager()

    with pytest.raises(NodeError):
        manager.activate(node)