import pytest

from influx.node_runtime.configuration import NodeConfiguration
from influx.node_runtime.errors import NodeConfigurationError


def test_valid_configuration() -> None:
    config = NodeConfiguration(
        node_id="node-1",
        network="testnet",
    )

    config.validate()


def test_missing_node_id() -> None:
    config = NodeConfiguration(
        node_id="",
        network="testnet",
    )

    with pytest.raises(NodeConfigurationError):
        config.validate()


def test_missing_network() -> None:
    config = NodeConfiguration(
        node_id="node-1",
        network="",
    )

    with pytest.raises(NodeConfigurationError):
        config.validate()