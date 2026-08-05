from influx.contracts.migration.migration import ContractMigration
from influx.contracts.migration.validator import MigrationValidator


def create_migration():
    return ContractMigration(
        migration_id="migration_001",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="2.0.0",
        description="Initial migration",
    )


def test_valid_migration_passes():

    validator = MigrationValidator()

    assert validator.validate(create_migration())


def test_missing_migration_id_fails():

    validator = MigrationValidator()

    migration = ContractMigration(
        migration_id="",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="2.0.0",
        description="Initial migration",
    )

    assert not validator.validate(migration)


def test_missing_contract_id_fails():

    validator = MigrationValidator()

    migration = ContractMigration(
        migration_id="migration_001",
        contract_id="",
        from_version="1.0.0",
        to_version="2.0.0",
        description="Initial migration",
    )

    assert not validator.validate(migration)


def test_same_version_fails():

    validator = MigrationValidator()

    migration = ContractMigration(
        migration_id="migration_001",
        contract_id="contract_a",
        from_version="2.0.0",
        to_version="2.0.0",
        description="No-op migration",
    )

    assert not validator.validate(migration)


def test_missing_description_fails():

    validator = MigrationValidator()

    migration = ContractMigration(
        migration_id="migration_001",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="2.0.0",
        description="",
    )

    assert not validator.validate(migration)


def test_validation_is_deterministic():

    validator = MigrationValidator()

    first = validator.validate(create_migration())
    second = validator.validate(create_migration())

    assert first == second