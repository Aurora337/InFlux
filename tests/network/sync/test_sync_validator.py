from influx.network.sync.sync_snapshot import SyncSnapshot
from influx.network.sync.sync_validator import SyncValidator


def test_valid_snapshot():

    validator = SyncValidator()

    snapshot = SyncSnapshot(
        snapshot_id="snap-1",
        height=5,
        state_hash="abc123",
    )

    assert validator.validate(snapshot)


def test_invalid_height():

    validator = SyncValidator()

    snapshot = SyncSnapshot(
        snapshot_id="snap-1",
        height=-1,
        state_hash="abc123",
    )

    assert not validator.validate(snapshot)