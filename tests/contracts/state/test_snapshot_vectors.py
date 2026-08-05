from influx.contracts.state.snapshot import StateSnapshot


def create_snapshot():
    return StateSnapshot(
        contract_id="contract_a",
        version="1.0.0",
        state={
            "balance": 100,
            "owner": "validator_001",
        },
        height=10,
    )


def test_snapshot_creation():

    snapshot = create_snapshot()

    assert snapshot.contract_id == "contract_a"


def test_snapshot_export():

    snapshot = create_snapshot()

    data = snapshot.to_dict()

    assert data["height"] == 10
    assert data["version"] == "1.0.0"


def test_snapshot_keys_are_sorted():

    snapshot = create_snapshot()

    assert snapshot.keys() == [
        "balance",
        "owner",
    ]


def test_identical_snapshots_match():

    first = create_snapshot()
    second = create_snapshot()

    assert first.same_state(second)


def test_different_states_do_not_match():

    first = create_snapshot()

    second = StateSnapshot(
        contract_id="contract_a",
        version="1.0.0",
        state={
            "balance": 200,
            "owner": "validator_001",
        },
        height=10,
    )

    assert not first.same_state(second)


def test_snapshot_is_immutable():

    snapshot = create_snapshot()

    try:
        snapshot.height = 20
    except Exception:
        assert True
    else:
        assert False