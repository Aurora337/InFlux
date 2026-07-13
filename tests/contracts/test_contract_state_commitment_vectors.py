from influx.crypto.hash import DeterministicHasher
from influx.contracts.storage import ContractStorage


def contract_state_root(storage: ContractStorage) -> str:
    return DeterministicHasher.hash(
        storage.snapshot()
    )


def test_identical_storage_produces_identical_root():
    storage_a = ContractStorage()
    storage_b = ContractStorage()

    storage_a.put("balance", "100")
    storage_b.put("balance", "100")

    assert (
        contract_state_root(storage_a)
        ==
        contract_state_root(storage_b)
    )


def test_storage_change_changes_root():
    storage = ContractStorage()

    storage.put(
        "balance",
        "100",
    )

    root_before = contract_state_root(storage)

    storage.put(
        "balance",
        "200",
    )

    root_after = contract_state_root(storage)

    assert root_before != root_after


def test_replaying_same_storage_produces_same_root():
    storage_a = ContractStorage()
    storage_b = ContractStorage()

    for storage in (storage_a, storage_b):
        storage.put("owner", "validator")
        storage.put("supply", "1000")

    assert (
        contract_state_root(storage_a)
        ==
        contract_state_root(storage_b)
    )


def test_storage_order_does_not_change_root():
    storage_a = ContractStorage()
    storage_b = ContractStorage()

    storage_a.put("a", "1")
    storage_a.put("b", "2")

    storage_b.put("b", "2")
    storage_b.put("a", "1")

    assert (
        contract_state_root(storage_a)
        ==
        contract_state_root(storage_b)
    )


def test_storage_corruption_changes_root():
    storage = ContractStorage()

    storage.put(
        "state",
        "valid",
    )

    valid_root = contract_state_root(storage)

    storage.put(
        "state",
        "corrupted",
    )

    corrupted_root = contract_state_root(storage)

    assert valid_root != corrupted_root