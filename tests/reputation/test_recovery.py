from influx.reputation.recovery_manager import (
    RecoveryManager,
    RecoveryState,
)


def test_begin_recovery():

    manager = RecoveryManager()

    state = manager.begin(
        "node-1",
    )

    assert isinstance(
        state,
        RecoveryState,
    )

    assert (
        state.validator_id
        == "node-1"
    )

    assert (
        state.recovered
        is False
    )


def test_complete_recovery():

    manager = RecoveryManager()

    manager.begin(
        "node-1",
    )

    result = manager.recover(
        "node-1",
    )

    assert result is True

    state = manager.status(
        "node-1",
    )

    assert state is not None

    assert (
        state.recovered
        is True
    )


def test_unknown_recovery():

    manager = RecoveryManager()

    assert (
        manager.recover(
            "missing"
        )
        is False
    )


def test_missing_status():

    manager = RecoveryManager()

    assert (
        manager.status(
            "missing"
        )
        is None
    )