from influx.security.consensus_guard import (
    ConsensusGuard,
    GuardDecision,
)


def test_validator_allowed():

    guard = ConsensusGuard()

    decision = guard.evaluate(
        validator_id="node-1",
        faults=1,
    )

    assert isinstance(
        decision,
        GuardDecision,
    )

    assert (
        decision.allowed
        is True
    )

    assert (
        decision.reason
        == "validator_safe"
    )


def test_validator_blocked():

    guard = ConsensusGuard()

    decision = guard.evaluate(
        validator_id="node-1",
        faults=5,
    )

    assert (
        decision.allowed
        is False
    )

    assert (
        decision.reason
        == "fault_threshold_exceeded"
    )


def test_custom_fault_threshold():

    guard = ConsensusGuard()

    decision = guard.evaluate(
        validator_id="node-1",
        faults=2,
        threshold=2,
    )

    assert (
        decision.allowed
        is False
    )