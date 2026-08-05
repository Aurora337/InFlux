from influx.network.sync.sync_snapshot import SyncSnapshot


def test_defaults():

    snapshot = SyncSnapshot(
        snapshot_id="snap-1",
        height=10,
        state_hash="abc123",
    )

    assert snapshot.height == 10


def test_snapshot():

    snapshot = SyncSnapshot(
        snapshot_id="snap-1",
        height=10,
        state_hash="abc123",
    )

    assert "state_hash" in snapshot.snapshot()