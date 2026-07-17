from influx.network.message import NetworkMessage
from influx.network.queue import MessageQueue


def create_message(message_id: str) -> NetworkMessage:
    return NetworkMessage(
        message_id=message_id,
        message_type="PING",
        sender_id="node-a",
        receiver_id="node-b",
        epoch=1,
        slot=1,
        timestamp=123456789,
        payload={},
    )


def test_enqueue_dequeue() -> None:
    queue = MessageQueue()

    message = create_message("msg-1")

    queue.enqueue(message)

    assert queue.dequeue() == message


def test_fifo_order() -> None:
    queue = MessageQueue()

    a = create_message("a")
    b = create_message("b")
    c = create_message("c")

    queue.enqueue(a)
    queue.enqueue(b)
    queue.enqueue(c)

    assert queue.dequeue() == a
    assert queue.dequeue() == b
    assert queue.dequeue() == c


def test_peek() -> None:
    queue = MessageQueue()

    message = create_message("peek")

    queue.enqueue(message)

    assert queue.peek() == message
    assert queue.size() == 1


def test_empty_queue() -> None:
    queue = MessageQueue()

    assert queue.empty()
    assert queue.dequeue() is None
    assert queue.peek() is None


def test_clear() -> None:
    queue = MessageQueue()

    queue.enqueue(create_message("1"))
    queue.enqueue(create_message("2"))

    assert queue.size() == 2

    queue.clear()

    assert queue.empty()
    assert queue.size() == 0