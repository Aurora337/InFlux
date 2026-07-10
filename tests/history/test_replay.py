from influx.history.state_history import (
    StateHistory,
)

from influx.history.replay_engine import (
    ReplayEngine,
)


def test_replay_state():

    history = StateHistory()

    history.record(
        10,
        {
            "alice": 100,
        },
        "root10",
    )

    engine = ReplayEngine(
        history
    )

    state = engine.replay(
        10
    )

    assert state is not None

    assert (
        state["alice"]
        == 100
    )


def test_missing_replay():

    history = StateHistory()

    engine = ReplayEngine(
        history
    )

    assert (
        engine.replay(
            99
        )
        is None
    )


def test_verify_root():

    history = StateHistory()

    history.record(
        5,
        {
            "node": 1,
        },
        "root5",
    )

    engine = ReplayEngine(
        history
    )

    assert engine.verify(
        5,
        "root5",
    )


def test_invalid_root():

    history = StateHistory()

    history.record(
        5,
        {},
        "correct",
    )

    engine = ReplayEngine(
        history
    )

    assert (
        engine.verify(
            5,
            "wrong",
        )
        is False
    )