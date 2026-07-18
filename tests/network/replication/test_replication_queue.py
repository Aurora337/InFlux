from influx.network.replication.replication_message import (
    ReplicationMessage,
)

from influx.network.replication.replication_queue import (
    ReplicationQueue,
)


def create_message():

    return ReplicationMessage(
        sender="node-1",
        payload="block",
    )


def test_enqueue():

    queue = ReplicationQueue()

    assert queue.enqueue(
        create_message()
    )

    assert queue.size() == 1


def test_dequeue():

    queue = ReplicationQueue()

    queue.enqueue(
        create_message()
    )

    message = queue.dequeue()

    assert message is not None

    assert queue.empty()


def test_empty_queue():

    queue = ReplicationQueue()

    assert queue.dequeue() is None