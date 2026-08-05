from influx.state_sync.state_diff import (
    StateDiff,
)

from influx.state_sync.sync_protocol import (
    SyncProtocol,
)


def test_create_package():

    protocol = SyncProtocol()

    diff = StateDiff(
        added={
            "alice": 100,
        }
    )

    package = protocol.create_package(
        "old_root",
        "new_root",
        diff,
    )

    assert (
        "diff"
        in package
    )

    assert (
        "proof"
        in package
    )


def test_validate_package():

    protocol = SyncProtocol()

    diff = StateDiff(
        modified={
            "alice": 200,
        }
    )

    package = protocol.create_package(
        "old",
        "new",
        diff,
    )

    assert protocol.validate_package(
        package
    )


def test_reject_invalid_package():

    protocol = SyncProtocol()

    diff = StateDiff(
        added={
            "alice": 100,
        }
    )

    package = protocol.create_package(
        "old",
        "new",
        diff,
    )

    package["diff"] = StateDiff(
        added={
            "alice": 999,
        }
    )

    assert (
        protocol.validate_package(
            package
        )
        is False
    )