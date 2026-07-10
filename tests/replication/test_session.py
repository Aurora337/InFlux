from influx.replication.checkpoint import Checkpoint
from influx.replication.replication_session import ReplicationSession
from influx.replication.replication_state import ReplicationState


def create_checkpoint() -> Checkpoint:
    return Checkpoint(
        checkpoint_id="checkpoint-1",
        height=42,
        state_hash="abc123",
    )


def create_session() -> ReplicationSession:
    return ReplicationSession(
        session_id="session-1",
        source_node="node-a",
        target_node="node-b",
        checkpoint=create_checkpoint(),
    )


def test_session_defaults():

    session = create_session()

    assert session.session_id == "session-1"
    assert session.source_node == "node-a"
    assert session.target_node == "node-b"
    assert session.state == ReplicationState.CREATED
    assert session.completed_at is None
    assert not session.verified


def test_start():

    session = create_session()

    session.start()

    assert session.state == ReplicationState.SYNCING


def test_verify():

    session = create_session()

    session.verify()

    assert session.state == ReplicationState.VERIFYING
    assert session.verified


def test_commit():

    session = create_session()

    session.commit()

    assert session.state == ReplicationState.COMMITTED
    assert session.completed_at is not None


def test_fail():

    session = create_session()

    session.fail()

    assert session.state == ReplicationState.FAILED
    assert session.completed_at is not None


def test_cancel():

    session = create_session()

    session.cancel()

    assert session.state == ReplicationState.CANCELLED
    assert session.completed_at is not None


def test_snapshot():

    session = create_session()

    snapshot = session.snapshot()

    assert snapshot["session_id"] == "session-1"
    assert snapshot["source_node"] == "node-a"
    assert snapshot["target_node"] == "node-b"
    assert snapshot["state"] == "created"
    assert "checkpoint" in snapshot