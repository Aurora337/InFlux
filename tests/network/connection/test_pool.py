from influx.network.connection.connection import Connection
from influx.network.connection.connection_pool import ConnectionPool
from influx.network.peer import Peer


def test_pool_allocate():

    pool = ConnectionPool()

    peer = Peer(
        node_id="node1",
        address="10.0.0.1",
        port=9000,
    )

    connection = Connection(
        "conn1",
        peer,
    )

    pool.allocate(connection)

    assert len(pool.available()) == 1


def test_pool_cleanup():

    pool = ConnectionPool()

    peer = Peer(
        node_id="node1",
        address="10.0.0.1",
        port=9000,
    )

    connection = Connection(
        "conn1",
        peer,
    )

    pool.allocate(connection)

    pool.cleanup()

    assert len(pool.available()) == 0