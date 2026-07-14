import pytest

from influx.contracts.migration.executor import MigrationExecutor
from influx.contracts.migration.migration import ContractMigration


def create_migration(version: str = "2.0.0"):
    return ContractMigration(
        migration_id=f"migration_{version}",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version=version,
        description="Migration",
    )


def test_execute_valid_migration():

    executor = MigrationExecutor()

    assert executor.execute(create_migration())
    assert executor.count() == 1


def test_invalid_migration_is_rejected():

    executor = MigrationExecutor()

    invalid = ContractMigration(
        migration_id="",
        contract_id="contract_a",
        from_version="1.0.0",
        to_version="2.0.0",
        description="Migration",
    )

    assert not executor.execute(invalid)
    assert executor.count() == 0


def test_latest_migration():

    executor = MigrationExecutor()

    first = create_migration("2.0.0")

    second = ContractMigration(
        migration_id="migration_3",
        contract_id="contract_a",
        from_version="2.0.0",
        to_version="3.0.0",
        description="Second migration",
    )

    executor.execute(first)
    executor.execute(second)

    assert executor.latest().to_version == "3.0.0"


def test_latest_requires_execution():

    executor = MigrationExecutor()

    with pytest.raises(ValueError):
        executor.latest()


def test_multiple_migrations_are_recorded():

    executor = MigrationExecutor()

    executor.execute(create_migration("2.0.0"))

    executor.execute(
        ContractMigration(
            migration_id="migration_3",
            contract_id="contract_a",
            from_version="2.0.0",
            to_version="3.0.0",
            description="Second migration",
        )
    )

    assert executor.count() == 2


def test_execution_is_deterministic():

    executor_a = MigrationExecutor()
    executor_b = MigrationExecutor()

    executor_a.execute(create_migration())
    executor_b.execute(create_migration())

    assert (
        executor_a.latest().to_dict()
        ==
        executor_b.latest().to_dict()
    )