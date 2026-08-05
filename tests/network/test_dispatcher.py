from influx.network.dispatcher import MessageDispatcher
from influx.network.message import NetworkMessage


def create_message(message_type: str = "PING") -> NetworkMessage:
    return NetworkMessage(
        message_id="msg-1",
        message_type=message_type,
        sender_id="node-a",
        receiver_id="node-b",
        epoch=1,
        slot=1,
        timestamp=123456789,
        payload={},
    )


def test_register_and_dispatch() -> None:
    dispatcher = MessageDispatcher()

    received: list[str] = []

    def handler(message: NetworkMessage) -> None:
        received.append(message.message_id)

    dispatcher.register("PING", handler)

    dispatcher.dispatch(create_message())

    assert received == ["msg-1"]


def test_unregister() -> None:
    dispatcher = MessageDispatcher()

    called = False

    def handler(message: NetworkMessage) -> None:
        nonlocal called
        called = True

    dispatcher.register("PING", handler)
    dispatcher.unregister("PING")

    dispatcher.dispatch(create_message())

    assert not called


def test_unknown_message_type() -> None:
    dispatcher = MessageDispatcher()

    assert dispatcher.dispatch(create_message("UNKNOWN")) is False


def test_clear() -> None:
    dispatcher = MessageDispatcher()

    dispatcher.register("PING", lambda m: None)
    dispatcher.register("PONG", lambda m: None)

    assert dispatcher.handler_count() == 2

    dispatcher.clear()

    assert dispatcher.handler_count() == 0