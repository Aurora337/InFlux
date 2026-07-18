from influx.network.replication.replication import (
    Replication,
)

from influx.network.replication.replication_state import (
    ReplicationState,
)


def test_queue():

    replication = Replication(
        replication_id="rep-1",
    )

    assert replication.queue()

    assert (
        replication.state
        is ReplicationState.QUEUED
    )


def test_start():

    replication = Replication(
        replication_id="rep-1",
    )

    replication.start()

    assert (
        replication.state
        is ReplicationState.REPLICATING
    )


def test_complete():

    replication = Replication(
        replication_id="rep-1",
    )

    result = replication.complete(3)

    assert result.success