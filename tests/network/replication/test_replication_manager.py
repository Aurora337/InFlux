from influx.network.replication.replication import Replication
from influx.network.replication.replication_manager import (
    ReplicationManager,
)
from influx.network.replication.replication_state import (
    ReplicationState,
)


def test_begin():
    manager = ReplicationManager()

    replication = Replication(
        replication_id="rep-1"
    )

    assert manager.begin(replication)

    assert (
        replication.state
        is ReplicationState.REPLICATING
    )


def test_complete():
    manager = ReplicationManager()

    replication = Replication(
        replication_id="rep-1"
    )

    manager.begin(replication)

    assert manager.complete(
        replication,
        3,
    )

    assert (
        manager.metrics.tasks_completed
        == 1
    )

    assert (
        manager.metrics.replicas_written
        == 3
    )