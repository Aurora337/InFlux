from influx.network.consensus.consensus_message import (
    ConsensusMessage,
)


def test_defaults():
    message = ConsensusMessage(
        sender="node-1",
        payload="block",
    )

    assert message.sender == "node-1"


def test_snapshot():
    message = ConsensusMessage(
        sender="node-1",
        payload="block",
    )

    assert "payload" in message.snapshot()