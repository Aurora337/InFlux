from influx.network.address import NetworkAddress
from influx.network.message import NetworkMessage
from influx.network.peer import Peer
from influx.network.registry import PeerRegistry
from influx.network.router import MessageRouter


def create_peer(node_id: str) -> Peer:
    return Peer(
        node_id=node_id,
        address=NetworkAddress(
            "localhost",
            9000,
        ),
    )


def create_message(receiver: str) -> NetworkMessage:
    return NetworkMessage(
        message_id="msg-1",
        message_type="PING",
        sender_id="node-a",
        receiver_id=receiver,
        epoch=1,
        slot=1,
        timestamp=123456789,
        payload={"hello": "world"},
    )


def test_route_existing_peer() -> None:
    registry = PeerRegistry()

    registry.register(
        create_peer("node-b")
    )

    router = MessageRouter(registry)

    message = create_message(
        "node-b"
    )

    assert router.route(message)


def test_route_missing_peer() -> None:
    registry = PeerRegistry()

    router = MessageRouter(registry)

    message = create_message(
        "missing"
    )

    assert not router.route(message)


def test_route_multiple_peers() -> None:
    registry = PeerRegistry()

    registry.register(
        create_peer("node-a")
    )

    registry.register(
        create_peer("node-b")
    )

    router = MessageRouter(registry)

    assert router.route(
        create_message("node-b")
    )