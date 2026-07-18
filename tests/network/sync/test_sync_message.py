from influx.network.sync.sync_message import SyncMessage


def test_defaults():

    message = SyncMessage(
        sender="node-1",
        receiver="node-2",
        payload="sync",
    )

    assert message.sender == "node-1"


def test_snapshot():

    message = SyncMessage(
        sender="node-1",
        receiver="node-2",
        payload="sync",
    )

    assert "receiver" in message.snapshot()