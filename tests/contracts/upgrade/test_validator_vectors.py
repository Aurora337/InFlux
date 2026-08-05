from influx.contracts.upgrade.record import UpgradeRecord
from influx.contracts.upgrade.validator import UpgradeValidator


def create_record():
    return UpgradeRecord(
        contract_id="contract_a",
        previous_version="1.0.0",
        new_version="2.0.0",
        migration_id="migration_001",
        height=100,
    )


def test_valid_upgrade_passes():

    validator = UpgradeValidator()

    assert validator.validate(create_record())


def test_missing_contract_id_fails():

    validator = UpgradeValidator()

    record = UpgradeRecord(
        contract_id="",
        previous_version="1.0.0",
        new_version="2.0.0",
        migration_id="migration_001",
        height=100,
    )

    assert not validator.validate(record)


def test_missing_migration_id_fails():

    validator = UpgradeValidator()

    record = UpgradeRecord(
        contract_id="contract_a",
        previous_version="1.0.0",
        new_version="2.0.0",
        migration_id="",
        height=100,
    )

    assert not validator.validate(record)


def test_same_version_fails():

    validator = UpgradeValidator()

    record = UpgradeRecord(
        contract_id="contract_a",
        previous_version="2.0.0",
        new_version="2.0.0",
        migration_id="migration_001",
        height=100,
    )

    assert not validator.validate(record)


def test_missing_new_version_fails():

    validator = UpgradeValidator()

    record = UpgradeRecord(
        contract_id="contract_a",
        previous_version="1.0.0",
        new_version="",
        migration_id="migration_001",
        height=100,
    )

    assert not validator.validate(record)


def test_validation_is_deterministic():

    validator = UpgradeValidator()

    first = validator.validate(create_record())
    second = validator.validate(create_record())

    assert first == second