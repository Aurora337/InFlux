from influx.contracts.state import ContractState


def test_put_and_get():
    state = ContractState()

    state.put("balance", 100)

    assert state.get("balance") == 100


def test_delete():
    state = ContractState()

    state.put("balance", 100)
    state.delete("balance")

    assert state.get("balance") is None


def test_contains():
    state = ContractState()

    state.put("owner", "alice")

    assert state.contains("owner")
    assert not state.contains("missing")


def test_snapshot_is_deterministic():
    state = ContractState()

    state.put("z", 3)
    state.put("a", 1)
    state.put("m", 2)

    assert list(state.snapshot().keys()) == [
        "a",
        "m",
        "z",
    ]


def test_restore():
    state = ContractState()

    state.put("x", 10)

    snapshot = state.snapshot()

    restored = ContractState()
    restored.restore(snapshot)

    assert restored.snapshot() == snapshot


def test_clear():
    state = ContractState()

    state.put("a", 1)
    state.put("b", 2)

    state.clear()

    assert state.size() == 0