from influx.replication.state_diff import StateDiff


def test_compare_empty():

    assert StateDiff.compare({}, {}) == {}


def test_compare_changed_value():

    old = {
        "balance": 100,
    }

    new = {
        "balance": 150,
    }

    diff = StateDiff.compare(
        old,
        new,
    )

    assert diff == {
        "balance": {
            "old": 100,
            "new": 150,
        }
    }


def test_compare_added_key():

    diff = StateDiff.compare(
        {},
        {
            "height": 1,
        },
    )

    assert diff["height"]["old"] is None
    assert diff["height"]["new"] == 1


def test_apply():

    state = {
        "height": 5,
        "balance": 100,
    }

    diff = {
        "balance": {
            "old": 100,
            "new": 250,
        }
    }

    updated = StateDiff.apply(
        state,
        diff,
    )

    assert updated["height"] == 5
    assert updated["balance"] == 250


def test_apply_empty():

    state = {
        "height": 10,
    }

    updated = StateDiff.apply(
        state,
        {},
    )

    assert updated == state


def test_is_empty():

    assert StateDiff.is_empty({})

    assert not StateDiff.is_empty(
        {
            "a": {
                "old": 1,
                "new": 2,
            }
        }
    )