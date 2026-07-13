from influx.contracts.snapshot import ContractSnapshot
from influx.contracts.state import ContractState


def create_state():
    state = ContractState()

    state.put("owner", "alice")
    state.put("balance", 100)
    state.put("nonce", 7)

    return state


def test_snapshot_creation():
    state = create_state()

    snapshot = ContractSnapshot.create(state)

    assert snapshot.size() == 3


def test_snapshot_restore():
    state = create_state()

    snapshot = ContractSnapshot.create(state)

    state.put("balance", 999)

    snapshot.restore(state)

    assert state.get("balance") == 100


def test_snapshot_is_deterministic():
    state1 = create_state()
    state2 = create_state()

    snap1 = ContractSnapshot.create(state1)
    snap2 = ContractSnapshot.create(state2)

    assert snap1.values == snap2.values


def test_snapshot_is_immutable():
    state = create_state()

    snap = ContractSnapshot.create(state)

    state.put("balance", 500)

    assert snap.values["balance"] == 100


def test_multiple_restores():
    state = create_state()

    snap = ContractSnapshot.create(state)

    state.clear()

    snap.restore(state)
    snap.restore(state)

    assert state.snapshot() == snap.values


def test_snapshot_preserves_order():
    state = ContractState()

    state.put("z", 1)
    state.put("a", 2)
    state.put("m", 3)

    snap = ContractSnapshot.create(state)

    assert list(snap.values.keys()) == [
        "a",
        "m",
        "z",
    ]