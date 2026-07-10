from influx.network.synchronization.sync_message import (
    SyncMessage,
)


def test_message_defaults():

    message = SyncMessage(
        source_node="node-a",
        target_node="node-b",
        payload={
            "type": "sync",
        },
    )

    assert message.source_node == "node-a"
    assert message.target_node == "node-b"
    assert message.state_hash == ""


def test_message_id_created():

    message = SyncMessage(
        source_node="node-a",
        target_node="node-b",
        payload={},
    )

    assert message.message_id is not None


def test_message_snapshot():

    message = SyncMessage(
        source_node="node-a",
        target_node="node-b",
        payload={
            "state": "request",
        },
        state_hash="abc123",
    )

    snapshot = message.snapshot()

    assert snapshot["source_node"] == "node-a"
    assert snapshot["target_node"] == "node-b"
    assert snapshot["state_hash"] == "abc123"
    assert "message_id" in snapshot