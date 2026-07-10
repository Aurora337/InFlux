from influx.replication.checkpoint import Checkpoint
from influx.replication.replication_policy import ReplicationPolicy
from influx.replication.replication_session import ReplicationSession
from influx.replication.replication_validator import ReplicationValidator


def create_checkpoint():

    return Checkpoint(
        checkpoint_id="cp-1",
        height=10,
        state_hash="abc123",
    )


def create_session():

    return ReplicationSession(
        session_id="session-1",
        source_node="node-a",
        target_node="node-b",
        checkpoint=create_checkpoint(),
    )


def test_valid_checkpoint():

    validator = ReplicationValidator()

    assert validator.validate_checkpoint(
        create_checkpoint()
    )


def test_invalid_checkpoint():

    validator = ReplicationValidator()

    checkpoint = Checkpoint(
        checkpoint_id="",
        height=-1,
        state_hash="",
    )

    assert not validator.validate_checkpoint(
        checkpoint
    )


def test_valid_session():

    validator = ReplicationValidator()

    assert validator.validate_session(
        create_session()
    )


def test_same_source_target():

    validator = ReplicationValidator()

    checkpoint = create_checkpoint()

    session = ReplicationSession(
        session_id="session-1",
        source_node="node-a",
        target_node="node-a",
        checkpoint=checkpoint,
    )

    assert not validator.validate_session(
        session
    )


def test_policy_limit():

    policy = ReplicationPolicy(
        max_concurrent_sessions=2,
    )

    validator = ReplicationValidator(
        policy
    )

    assert validator.validate_policy(0)

    assert validator.validate_policy(1)

    assert not validator.validate_policy(2)