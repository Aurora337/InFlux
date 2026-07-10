from influx.network.gossip.gossip import (
    Gossip,
)

from influx.network.gossip.gossip_message import (
    GossipMessage,
)

from influx.network.gossip.gossip_state import (
    GossipState,
)


def create_message():

    return GossipMessage(
        origin="node-1",
        payload={
            "event": "hello",
        },
    )


def test_gossip_defaults():

    gossip = Gossip()

    assert (
        gossip.state
        == GossipState.INITIALIZING
    )


def test_start():

    gossip = Gossip()

    gossip.start()

    assert (
        gossip.state
        == GossipState.ACTIVE
    )


def test_receive_message():

    gossip = Gossip()

    gossip.start()

    result = gossip.receive(
        create_message()
    )

    assert result

    assert (
        gossip.table.count()
        == 1
    )


def test_duplicate_message():

    gossip = Gossip()

    message = create_message()

    gossip.receive(
        message
    )

    result = gossip.receive(
        message
    )

    assert not result


def test_lookup():

    gossip = Gossip()

    message = create_message()

    gossip.receive(
        message
    )

    found = gossip.lookup(
        message.message_id
    )

    assert found is message


def test_expired_message():

    gossip = Gossip()

    message = create_message()

    message.ttl = 0

    result = gossip.propagate(
        message
    )

    assert not result


def test_stop():

    gossip = Gossip()

    gossip.stop()

    assert (
        gossip.state
        == GossipState.STOPPED
    )


def test_snapshot():

    gossip = Gossip()

    snapshot = gossip.snapshot()

    assert "state" in snapshot
    assert "metrics" in snapshot