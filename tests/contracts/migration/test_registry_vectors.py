import pytest

from influx.contracts.migration.migration import ContractMigration
from influx.contracts.migration.registry import MigrationRegistry


def create_migration():
    return ContractMigration(
        migration_id="migration_001",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="2.0.0",
        description="Initial migration",
    )


def test_register_migration():

    registry = MigrationRegistry()

    assert registry.register(create_migration())
    assert registry.count() == 1


def test_duplicate_registration_fails():

    registry = MigrationRegistry()

    migration = create_migration()

    registry.register(migration)

    assert not registry.register(migration)


def test_get_registered_migration():

    registry = MigrationRegistry()

    migration = create_migration()

    registry.register(migration)

    assert registry.get("migration_001") == migration


def test_unknown_migration_raises():

    registry = MigrationRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_registration_is_deterministic():

    registry_a = MigrationRegistry()
    registry_b = MigrationRegistry()

    registry_a.register(create_migration())
    registry_b.register(create_migration())

    assert (
        registry_a.get("migration_001").to_dict()
        ==
        registry_b.get("migration_001").to_dict()
    )


def test_registry_count():

    registry = MigrationRegistry()

    registry.register(create_migration())

    registry.register(
        ContractMigration(
            migration_id="migration_002",
            contract_id="contract_a",
            from_version="2.0.0",
            to_version="3.0.0",
            description="Second migration",
        )
    )

    assert registry.count() == 2