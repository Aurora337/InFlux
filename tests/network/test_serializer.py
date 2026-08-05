from influx.network.message import NetworkMessage
from influx.network.serializer import MessageSerializer


def create_message() -> NetworkMessage:
    return NetworkMessage(
        message_id="msg-1",
        message_type="PING",
        sender_id="node-a",
        receiver_id="node-b",
        epoch=1,
        slot=1,
        timestamp=123456789,
        payload={"value": 42},
        state_hash="abc123",
        signature="sig",
    )


def test_serialize() -> None:
    message = create_message()

    data = MessageSerializer.serialize(message)

    assert isinstance(data, str)
    assert '"message_id":"msg-1"' in data


def test_deserialize() -> None:
    message = create_message()

    serialized = MessageSerializer.serialize(message)

    restored = MessageSerializer.deserialize(serialized)

    assert restored.message_id == message.message_id
    assert restored.sender_id == message.sender_id
    assert restored.receiver_id == message.receiver_id
    assert restored.message_type == message.message_type
    assert restored.payload == message.payload
    assert restored.state_hash == message.state_hash
    assert restored.signature == message.signature