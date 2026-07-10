from influx.history.state_history import (
    StateHistory,
)

from influx.history.historical_query import (
    HistoricalQuery,
)


def test_query_state():

    history = StateHistory()

    history.record(
        20,
        {
            "balance": 500,
        },
        "root20",
    )

    query = HistoricalQuery(
        history
    )

    state = query.state_at(
        20
    )

    assert state is not None

    assert (
        state["balance"]
        == 500
    )


def test_query_root():

    history = StateHistory()

    history.record(
        20,
        {},
        "root20",
    )

    query = HistoricalQuery(
        history
    )

    assert (
        query.root_at(
            20
        )
        ==
        "root20"
    )


def test_query_exists():

    history = StateHistory()

    history.record(
        1,
        {},
        "root",
    )

    query = HistoricalQuery(
        history
    )

    assert query.exists(
        1
    )

    assert (
        query.exists(
            99
        )
        is False
    )


def test_missing_query():

    history = StateHistory()

    query = HistoricalQuery(
        history
    )

    assert (
        query.state_at(
            50
        )
        is None
    )