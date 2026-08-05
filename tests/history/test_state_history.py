from influx.history.state_history import (
    HistoricalState,
    StateHistory,
)


def test_record_history():

    history = StateHistory()

    state = history.record(
        height=1,
        state={
            "alice": 100,
        },
        root_hash="root1",
    )

    assert isinstance(
        state,
        HistoricalState,
    )

    assert (
        state.height
        == 1
    )


def test_get_history():

    history = StateHistory()

    history.record(
        height=5,
        state={
            "node": 5,
        },
        root_hash="root5",
    )

    result = history.get(
        5
    )

    assert result is not None

    assert (
        result.root_hash
        == "root5"
    )


def test_latest_history():

    history = StateHistory()

    history.record(
        1,
        {},
        "root1",
    )

    history.record(
        10,
        {},
        "root10",
    )

    latest = history.latest()

    assert latest is not None

    assert (
        latest.height
        == 10
    )


def test_height_ordering():

    history = StateHistory()

    history.record(
        3,
        {},
        "a",
    )

    history.record(
        1,
        {},
        "b",
    )

    history.record(
        2,
        {},
        "c",
    )

    assert (
        history.heights()
        ==
        [1, 2, 3]
    )