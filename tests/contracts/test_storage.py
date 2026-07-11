from influx.contracts.storage import ContractStorage


def test_storage_operations() -> None:
    storage = ContractStorage()

    storage.put("key", "value")

    assert storage.contains("key")
    assert storage.get("key") == "value"

    storage.remove("key")

    assert not storage.contains("key")


def test_snapshot_sorted() -> None:
    storage = ContractStorage()

    storage.put("b", "2")
    storage.put("a", "1")

    snapshot = storage.snapshot()

    assert list(snapshot.keys()) == ["a", "b"]