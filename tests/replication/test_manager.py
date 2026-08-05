from influx.replication.checkpoint import Checkpoint
from influx.replication.replication_manager import ReplicationManager
from influx.replication.replication_session import ReplicationSession


def create_session(session_id: str = "session-1") -> ReplicationSession:

    checkpoint = Checkpoint(
        checkpoint_id="cp-1",
        height=1,
        state_hash="hash-1",
    )

    return ReplicationSession(
        session_id=session_id,
        source_node="node-a",
        target_node="node-b",
        checkpoint=checkpoint,
    )


def test_create():

    manager = ReplicationManager()

    assert manager.create(
        create_session()
    )


def test_duplicate():

    manager = ReplicationManager()

    session = create_session()

    manager.create(session)

    assert not manager.create(session)


def test_lookup():

    manager = ReplicationManager()

    session = create_session()

    manager.create(session)

    assert (
        manager.lookup("session-1")
        is session
    )


def test_remove():

    manager = ReplicationManager()

    session = create_session()

    manager.create(session)

    assert manager.remove(
        "session-1"
    )

    assert (
        manager.lookup("session-1")
        is None
    )


def test_active():

    manager = ReplicationManager()

    session = create_session()

    manager.create(session)

    assert len(
        manager.active()
    ) == 1


def test_completed():

    manager = ReplicationManager()

    session = create_session()

    session.commit()

    manager.create(session)

    assert len(
        manager.completed()
    ) == 1


def test_snapshot():

    manager = ReplicationManager()

    manager.create(
        create_session()
    )

    snapshot = manager.snapshot()

    assert "session-1" in snapshot