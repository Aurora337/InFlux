from influx.network.gossip.gossip_message import (
    GossipMessage,
)


def test_message_defaults():

    message = GossipMessage(
        origin="node-1",
        payload={
            "event": "hello",
        },
    )

    assert message.origin == "node-1"
    assert message.ttl == 8
    assert message.hops == 0


def test_message_id_created():

    message = GossipMessage(
        origin="node-1",
        payload={},
    )

    assert message.message_id is not None


def test_decrement_ttl():

    message = GossipMessage(
        origin="node-1",
        payload={},
    )

    result = message.decrement_ttl()

    assert result
    assert message.ttl == 7
    assert message.hops == 1


def test_expired_message():

    message = GossipMessage(
        origin="node-1",
        payload={},
        ttl=0,
    )

    assert message.expired()


def test_snapshot():

    message = GossipMessage(
        origin="node-1",
        payload={
            "type": "test",
        },
    )

    snapshot = message.snapshot()

    assert snapshot["origin"] == "node-1"
    assert "message_id" in snapshot