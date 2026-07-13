from influx.contracts.checkpoint import ContractCheckpointManager
from influx.contracts.rollback import ContractRollbackManager
from influx.contracts.state import ContractState


def create_environment():
    state = ContractState()

    state.put("balance", 100)
    state.put("nonce", 1)

    checkpoints = ContractCheckpointManager()
    checkpoints.create(
        "safe",
        state,
    )

    rollback = ContractRollbackManager(
        checkpoints,
    )

    return state, rollback


def test_valid_rollback_restores_state():
    state, rollback = create_environment()

    state.put("balance", 500)

    rollback.rollback(
        "safe",
        state,
    )

    assert state.get("balance") == 100


def test_invalid_checkpoint_is_rejected():
    state, rollback = create_environment()

    try:
        rollback.rollback(
            "missing",
            state,
        )
    except ValueError:
        assert True
    else:
        assert False


def test_can_rollback_detects_existing_checkpoint():
    _, rollback = create_environment()

    assert rollback.can_rollback("safe")


def test_can_rollback_rejects_unknown_checkpoint():
    _, rollback = create_environment()

    assert not rollback.can_rollback("missing")


def test_multiple_rollbacks_are_deterministic():
    state, rollback = create_environment()

    state.put("balance", 999)

    rollback.rollback("safe", state)
    first = state.snapshot()

    state.put("balance", 888)

    rollback.rollback("safe", state)
    second = state.snapshot()

    assert first == second


def test_rollback_preserves_checkpoint():
    state, rollback = create_environment()

    rollback.rollback(
        "safe",
        state,
    )

    assert rollback.can_rollback("safe")