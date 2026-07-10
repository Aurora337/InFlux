from influx.network.connection.connection_validator import ConnectionValidator
from influx.network.connection.connection_policy import ConnectionPolicy
from influx.network.peer import Peer


def test_valid_peer():

    validator = ConnectionValidator(
        ConnectionPolicy()
    )

    peer = Peer(
        node_id="node1",
        address="10.0.0.5",
        port=9000,
    )

    assert validator.validate_peer(peer)


def test_invalid_port():

    validator = ConnectionValidator(
        ConnectionPolicy()
    )

    peer = Peer(
        node_id="node1",
        address="10.0.0.5",
        port=70000,
    )

    assert not validator.validate_peer(peer)