from influx.contracts.persistence import ContractPersistence


def create_metadata(version: str = "1.0.0"):
    return {
        "owner": "validator_001",
        "version": version,
        "code_hash": "abc123def456",
    }


def test_save_and_load_contract():
    persistence = ContractPersistence()

    persistence.save(
        "contract_a",
        create_metadata(),
    )

    loaded = persistence.load("contract_a")

    assert loaded == create_metadata()


def test_contract_exists_after_save():
    persistence = ContractPersistence()

    persistence.save(
        "contract_a",
        create_metadata(),
    )

    assert persistence.exists("contract_a")


def test_remove_contract():
    persistence = ContractPersistence()

    persistence.save(
        "contract_a",
        create_metadata(),
    )

    persistence.remove("contract_a")

    assert not persistence.exists("contract_a")


def test_persistence_count():
    persistence = ContractPersistence()

    persistence.save("a", create_metadata())
    persistence.save("b", create_metadata("2.0.0"))

    assert persistence.count() == 2


def test_snapshot_is_deterministic():
    persistence = ContractPersistence()

    persistence.save("b", create_metadata("2.0.0"))
    persistence.save("a", create_metadata("1.0.0"))

    snapshot = persistence.snapshot()

    assert list(snapshot.keys()) == ["a", "b"]


def test_loaded_metadata_is_copy():
    persistence = ContractPersistence()

    persistence.save(
        "contract_a",
        create_metadata(),
    )

    loaded = persistence.load("contract_a")
    loaded["owner"] = "attacker"

    assert persistence.load("contract_a")["owner"] == "validator_001"