from influx.contracts.state.history import StateHistory
from influx.contracts.state.snapshot import StateSnapshot


def create_snapshot(height):
    return StateSnapshot(
        contract_id="contract_a",
        version="1.0.0",
        state={
            "balance": height
        },
        height=height,
    )


def test_add_snapshot():

    history = StateHistory()

    history.add(
        create_snapshot(1)
    )

    assert history.count() == 1


def test_latest_snapshot():

    history = StateHistory()

    history.add(create_snapshot(1))
    history.add(create_snapshot(2))

    assert history.latest().height == 2


def test_get_snapshot_by_height():

    history = StateHistory()

    history.add(create_snapshot(5))

    assert history.get(5).height == 5


def test_unknown_height_fails():

    history = StateHistory()

    try:
        history.get(99)
    except ValueError:
        assert True
    else:
        assert False


def test_height_order_is_preserved():

    history = StateHistory()

    history.add(create_snapshot(1))
    history.add(create_snapshot(2))
    history.add(create_snapshot(3))

    assert history.heights() == [
        1,
        2,
        3,
    ]


def test_latest_requires_history():

    history = StateHistory()

    try:
        history.latest()
    except ValueError:
        assert True
    else:
        assert False