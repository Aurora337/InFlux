from influx.contracts.state.manager import StateManager


def create_manager():
    return StateManager()


def create_state():
    return {
        "balance": 100,
        "owner": "validator_001",
    }


def test_create_snapshot():

    manager = create_manager()

    snapshot = manager.snapshot(
        "contract_a",
        "1.0.0",
        create_state(),
        1,
    )

    assert snapshot.height == 1


def test_snapshot_is_recorded():

    manager = create_manager()

    manager.snapshot(
        "contract_a",
        "1.0.0",
        create_state(),
        1,
    )

    assert manager.current().height == 1


def test_commitment_generation():

    manager = create_manager()

    snapshot = manager.snapshot(
        "contract_a",
        "1.0.0",
        create_state(),
        1,
    )

    assert len(
        manager.commitment(snapshot)
    ) == 64


def test_valid_commitment_verifies():

    manager = create_manager()

    snapshot = manager.snapshot(
        "contract_a",
        "1.0.0",
        create_state(),
        1,
    )

    commitment = manager.commitment(snapshot)

    assert manager.verify(
        snapshot,
        commitment,
    )


def test_invalid_commitment_fails():

    manager = create_manager()

    snapshot = manager.snapshot(
        "contract_a",
        "1.0.0",
        create_state(),
        1,
    )

    assert not manager.verify(
        snapshot,
        "invalid",
    )


def test_multiple_states_are_tracked():

    manager = create_manager()

    manager.snapshot(
        "contract_a",
        "1.0.0",
        {"value": 1},
        1,
    )

    manager.snapshot(
        "contract_a",
        "1.0.0",
        {"value": 2},
        2,
    )

    assert manager.current().height == 2