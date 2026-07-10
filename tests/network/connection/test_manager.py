from influx.network.connection.connection import Connection
from influx.network.connection.connection_manager import ConnectionManager
from influx.network.peer import Peer


def test_manager_open_close():

    manager = ConnectionManager()

    peer = Peer(
        node_id="node1",
        address="192.168.1.10",
        port=9000,
    )

    connection = Connection(
        "conn1",
        peer,
    )

    assert manager.open(connection)

    assert manager.lookup("conn1")

    assert manager.close("conn1")