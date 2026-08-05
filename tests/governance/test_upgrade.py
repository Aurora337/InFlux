from influx.governance.upgrade_manager import (
    UpgradeManager,
    UpgradeRecord,
)


def test_schedule_upgrade():

    manager = UpgradeManager()

    upgrade = manager.schedule(
        "v2.8.0",
    )

    assert isinstance(
        upgrade,
        UpgradeRecord,
    )

    assert (
        upgrade.version
        == "v2.8.0"
    )

    assert (
        upgrade.activated
        is False
    )


def test_activate_upgrade():

    manager = UpgradeManager()

    manager.schedule(
        "v2.8.0",
    )

    result = manager.activate(
        "v2.8.0",
    )

    assert (
        result
        is True
    )

    assert (
        manager.history()[0].activated
        is True
    )


def test_missing_upgrade():

    manager = UpgradeManager()

    assert (
        manager.activate(
            "missing"
        )
        is False
    )


def test_upgrade_history():

    manager = UpgradeManager()

    manager.schedule(
        "v2.8.0",
    )

    manager.schedule(
        "v2.9.0",
    )

    assert (
        len(manager.history())
        == 2
    )