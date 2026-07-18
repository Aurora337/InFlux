from influx.network.sync.sync_message import SyncMessage
from influx.network.sync.sync_queue import SyncQueue


def create_message():

    return SyncMessage(
        sender="node-1",
        receiver="node-2",
        payload="sync",
    )


def test_enqueue():

    queue = SyncQueue()

    assert queue.enqueue(
        create_message()
    )

    assert queue.size() == 1


def test_dequeue():

    queue = SyncQueue()

    queue.enqueue(
        create_message()
    )

    message = queue.dequeue()

    assert message is not None

    assert queue.empty()


def test_empty_queue():

    queue = SyncQueue()

    assert queue.dequeue() is None