from influx.network.replication.replication_message import (
    ReplicationMessage,
)


def test_defaults():

    message = ReplicationMessage(
        sender="node-1",
        payload="block",
    )

    assert message.sender == "node-1"


def test_snapshot():

    message = ReplicationMessage(
        sender="node-1",
        payload="block",
    )

    assert "payload" in message.snapshot()