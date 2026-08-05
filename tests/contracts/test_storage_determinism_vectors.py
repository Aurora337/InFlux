from influx.contracts.storage import ContractStorage


def test_same_storage_inputs_produce_same_state():
    storage_a = ContractStorage()
    storage_b = ContractStorage()

    storage_a.put("balance", "100")
    storage_b.put("balance", "100")

    assert storage_a.snapshot() == storage_b.snapshot()


def test_storage_key_order_does_not_change_state():
    storage_a = ContractStorage()
    storage_b = ContractStorage()

    storage_a.put("a", "1")
    storage_a.put("b", "2")

    storage_b.put("b", "2")
    storage_b.put("a", "1")

    assert storage_a.snapshot() == storage_b.snapshot()


def test_storage_mutation_changes_snapshot():
    storage = ContractStorage()

    before = storage.snapshot()

    storage.put(
        "value",
        "updated",
    )

    after = storage.snapshot()

    assert before != after


def test_storage_missing_key_returns_none():
    storage = ContractStorage()

    assert storage.get("missing") is None


def test_storage_snapshot_is_deterministic():
    storage = ContractStorage()

    storage.put("x", "10")
    storage.put("y", "20")

    snapshot_a = storage.snapshot()
    snapshot_b = storage.snapshot()

    assert snapshot_a == snapshot_b