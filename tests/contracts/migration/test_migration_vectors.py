from influx.contracts.migration.migration import ContractMigration


def create_migration():
    return ContractMigration(
        migration_id="migration_001",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="2.0.0",
        description="Initial upgrade",
    )


def test_migration_creation():

    migration = create_migration()

    assert migration.contract_id == "contract_a"


def test_migration_export():

    migration = create_migration()

    data = migration.to_dict()

    assert data["migration_id"] == "migration_001"
    assert data["to_version"] == "2.0.0"


def test_version_change_detected():

    migration = create_migration()

    assert migration.is_upgrade()


def test_same_version_not_upgrade():

    migration = ContractMigration(
        migration_id="migration_001",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="1.0.0",
        description="No-op",
    )

    assert not migration.is_upgrade()


def test_migrations_are_deterministic():

    first = create_migration()
    second = create_migration()

    assert first.to_dict() == second.to_dict()


def test_migration_is_immutable():

    migration = create_migration()

    try:
        migration.to_version = "3.0.0"
    except Exception:
        assert True
    else:
        assert False