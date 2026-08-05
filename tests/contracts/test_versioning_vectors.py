from influx.contracts.state import ContractState
from influx.contracts.versioning import ContractVersionManager


def create_state():
    state = ContractState()

    state.put("balance", 100)
    state.put("nonce", 1)

    return state


def test_create_version():
    manager = ContractVersionManager()
    state = create_state()

    manager.create_version(
        1,
        state,
    )

    assert manager.exists(1)


def test_restore_version():
    manager = ContractVersionManager()
    state = create_state()

    manager.create_version(
        1,
        state,
    )

    state.put("balance", 500)

    manager.restore_version(
        1,
        state,
    )

    assert state.get("balance") == 100


def test_versions_are_sorted():
    manager = ContractVersionManager()
    state = create_state()

    manager.create_version(5, state)
    manager.create_version(1, state)
    manager.create_version(3, state)

    assert manager.versions() == [
        1,
        3,
        5,
    ]


def test_duplicate_version_fails():
    manager = ContractVersionManager()
    state = create_state()

    manager.create_version(
        1,
        state,
    )

    try:
        manager.create_version(
            1,
            state,
        )
    except ValueError:
        assert True
    else:
        assert False


def test_unknown_version_fails():
    manager = ContractVersionManager()
    state = create_state()

    try:
        manager.restore_version(
            99,
            state,
        )
    except ValueError:
        assert True
    else:
        assert False


def test_versioning_is_deterministic():
    manager_a = ContractVersionManager()
    manager_b = ContractVersionManager()

    state_a = create_state()
    state_b = create_state()

    manager_a.create_version(1, state_a)
    manager_b.create_version(1, state_b)

    assert manager_a.versions() == manager_b.versions()