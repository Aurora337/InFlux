import pytest

from influx.contracts.upgrade.controller import UpgradeController
from influx.contracts.upgrade.record import UpgradeRecord


def create_record(version: str = "2.0.0", height: int = 100):
    return UpgradeRecord(
        contract_id="contract_a",
        previous_version="1.0.0",
        new_version=version,
        migration_id=f"migration_{height}",
        height=height,
    )


def test_valid_upgrade_is_recorded():

    controller = UpgradeController()

    assert controller.upgrade(create_record())
    assert controller.count() == 1


def test_invalid_upgrade_is_rejected():

    controller = UpgradeController()

    invalid = UpgradeRecord(
        contract_id="",
        previous_version="1.0.0",
        new_version="2.0.0",
        migration_id="migration",
        height=100,
    )

    assert not controller.upgrade(invalid)
    assert controller.count() == 0


def test_latest_upgrade():

    controller = UpgradeController()

    controller.upgrade(create_record("2.0.0", 100))
    controller.upgrade(
        UpgradeRecord(
            contract_id="contract_a",
            previous_version="2.0.0",
            new_version="3.0.0",
            migration_id="migration_200",
            height=200,
        )
    )

    assert controller.latest().new_version == "3.0.0"


def test_latest_requires_history():

    controller = UpgradeController()

    with pytest.raises(ValueError):
        controller.latest()


def test_multiple_upgrades_are_tracked():

    controller = UpgradeController()

    controller.upgrade(create_record("2.0.0", 100))
    controller.upgrade(
        UpgradeRecord(
            contract_id="contract_a",
            previous_version="2.0.0",
            new_version="3.0.0",
            migration_id="migration_200",
            height=200,
        )
    )

    assert controller.count() == 2


def test_upgrade_process_is_deterministic():

    controller_a = UpgradeController()
    controller_b = UpgradeController()

    controller_a.upgrade(create_record())
    controller_b.upgrade(create_record())

    assert controller_a.latest().to_dict() == controller_b.latest().to_dict()