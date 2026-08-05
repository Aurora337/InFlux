from influx.network.connection.connection import Connection
from influx.network.peer import Peer


def create_connection():
    peer = Peer(
        node_id="node1",
        address="192.168.1.5",
        port=9000,
    )

    return Connection(
        "conn1",
        peer,
    )


def test_open_close():

    connection = create_connection()

    connection.connect()

    assert connection.connected

    connection.disconnect()

    assert not connection.connected


def test_heartbeat():

    connection = create_connection()

    connection.connect()

    assert connection.heartbeat()


def test_send_receive():

    connection = create_connection()

    connection.connect()

    connection.send(b"hello")
    connection.receive(b"world")

    assert connection.bytes_sent == 5
    assert connection.bytes_received == 5


def test_snapshot():

    connection = create_connection()

    snapshot = connection.snapshot()

    assert snapshot["connection_id"] == "conn1"