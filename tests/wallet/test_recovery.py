from influx.wallet.recovery import (
    RecoveryManager,
    RecoveryRecord,
)


def test_create_recovery_record():

    manager = RecoveryManager()

    record = manager.create(
        account_id="account-1",
        recovery_key="backup-key",
        created_at=100,
    )

    assert isinstance(
        record,
        RecoveryRecord,
    )

    assert (
        record.account_id
        == "account-1"
    )

    assert (
        record.active
        is True
    )


def test_get_recovery_record():

    manager = RecoveryManager()

    manager.create(
        "account-1",
        "backup-key",
        100,
    )

    record = manager.get(
        "account-1"
    )

    assert record is not None

    assert (
        record.recovery_key
        == "backup-key"
    )


def test_revoke_recovery():

    manager = RecoveryManager()

    record = manager.create(
        "account-1",
        "backup-key",
        100,
    )

    record.revoke()

    assert (
        record.active
        is False
    )


def test_restore_recovery():

    manager = RecoveryManager()

    record = manager.create(
        "account-1",
        "backup-key",
        100,
    )

    record.revoke()

    record.restore()

    assert (
        record.active
        is True
    )


def test_remove_recovery():

    manager = RecoveryManager()

    manager.create(
        "account-1",
        "backup-key",
        100,
    )

    removed = manager.remove(
        "account-1"
    )

    assert removed is True

    assert (
        manager.get(
            "account-1"
        )
        is None
    )