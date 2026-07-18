from influx.network.routing.message import Message
from influx.network.routing.message_queue import MessageQueue


def create_message():
    return Message(
        source="node-a",
        destination="node-b",
        payload={
            "event": "test",
        },
    )


def test_enqueue():
    queue = MessageQueue()

    message = create_message()

    queue.enqueue(
        message
    )

    assert queue.size() == 1


def test_dequeue():

    queue = MessageQueue()

    message = create_message()

    queue.enqueue(
        message
    )

    result = queue.dequeue()

    assert result == message


def test_snapshot():

    queue = MessageQueue()

    queue.enqueue(
        create_message()
    )

    snapshot = queue.snapshot()

    assert snapshot