from influx.network.gossip.gossip import (
    Gossip,
)

from influx.network.gossip.gossip_message import (
    GossipMessage,
)


def create_message() -> GossipMessage:
    return GossipMessage(
        message_id="msg-1",
        origin="node-1",
        payload={
            "data": "hello",
        },
        signature="signature-1",
    )


def test_initial_state() -> None:
    gossip = Gossip()

    assert gossip.state.value == "initializing"


def test_start() -> None:
    gossip = Gossip()

    result = gossip.start()

    assert result
    assert gossip.state.value == "active"


def test_propagate() -> None:
    gossip = Gossip()

    gossip.start()

    result = gossip.propagate(
        create_message()
    )

    assert result


def test_stop() -> None:
    gossip = Gossip()

    gossip.start()

    result = gossip.stop()

    assert result
    assert gossip.state.value == "stopped"