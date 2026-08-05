from influx.contracts.checkpoint import ContractCheckpointManager
from influx.contracts.state import ContractState


def create_state():
    state = ContractState()
    state.put("balance", 100)
    state.put("nonce", 1)
    return state


def test_checkpoint_creation():
    manager = ContractCheckpointManager()
    state = create_state()

    manager.create("genesis", state)

    assert manager.exists("genesis")


def test_checkpoint_restore():
    manager = ContractCheckpointManager()
    state = create_state()

    manager.create("save", state)

    state.put("balance", 999)

    manager.restore("save", state)

    assert state.get("balance") == 100


def test_multiple_checkpoints():
    manager = ContractCheckpointManager()
    state = create_state()

    manager.create("cp1", state)

    state.put("balance", 200)

    manager.create("cp2", state)

    assert manager.count() == 2


def test_checkpoint_names_are_sorted():
    manager = ContractCheckpointManager()
    state = create_state()

    manager.create("zeta", state)
    manager.create("alpha", state)
    manager.create("middle", state)

    assert manager.names() == [
        "alpha",
        "middle",
        "zeta",
    ]


def test_restore_does_not_remove_checkpoint():
    manager = ContractCheckpointManager()
    state = create_state()

    manager.create("save", state)

    manager.restore("save", state)

    assert manager.exists("save")


def test_checkpoint_is_deterministic():
    manager1 = ContractCheckpointManager()
    manager2 = ContractCheckpointManager()

    state1 = create_state()
    state2 = create_state()

    manager1.create("cp", state1)
    manager2.create("cp", state2)

    assert manager1.names() == manager2.names()