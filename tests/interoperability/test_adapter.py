from influx.interoperability.external_adapter import (
    ExternalAdapter,
    ExternalMessage,
)


def test_receive_message():

    adapter = ExternalAdapter()

    adapter.receive(
        ExternalMessage(
            network="external-net",
            payload={"ping": True},
        )
    )

    assert adapter.count() == 1


def test_message_storage():

    adapter = ExternalAdapter()

    adapter.receive(
        ExternalMessage(
            network="external-net",
            payload={"value": 5},
        )
    )

    messages = adapter.messages()

    assert len(messages) == 1
    assert messages[0].network == "external-net"


def test_messages_returns_copy():

    adapter = ExternalAdapter()

    adapter.receive(
        ExternalMessage(
            network="external-net",
            payload={},
        )
    )

    first = adapter.messages()
    second = adapter.messages()

    assert first is not second

    first.clear()

    assert adapter.count() == 1