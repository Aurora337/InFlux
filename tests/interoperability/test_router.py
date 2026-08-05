from influx.interoperability.message_router import (
    MessageRouter,
    NetworkMessage,
)


def test_send_message():

    router = MessageRouter()

    message = NetworkMessage(
        message_id="msg-1",
        source="cluster-a",
        destination="cluster-b",
        payload={"height": 10},
    )

    router.send(
        message,
    )

    assert (
        router.count()
        == 1
    )


def test_message_storage():

    router = MessageRouter()

    router.send(
        NetworkMessage(
            message_id="msg-1",
            source="a",
            destination="b",
            payload={},
        )
    )

    messages = router.messages()

    assert len(messages) == 1

    assert (
        messages[0].message_id
        == "msg-1"
    )


def test_messages_returns_copy():

    router = MessageRouter()

    router.send(
        NetworkMessage(
            message_id="msg-1",
            source="a",
            destination="b",
            payload={},
        )
    )

    first = router.messages()
    second = router.messages()

    assert first is not second

    first.clear()

    assert (
        router.count()
        == 1
    )