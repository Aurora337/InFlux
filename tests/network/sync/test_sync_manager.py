from influx.network.sync.sync_manager import SyncManager
from influx.network.sync.sync_snapshot import SyncSnapshot


def test_synchronize():

    manager = SyncManager()

    snapshot = SyncSnapshot(
        snapshot_id="snap-1",
        height=1,
        state_hash="abc123",
    )

    assert manager.synchronize(snapshot)


def test_invalid_snapshot():

    manager = SyncManager()

    snapshot = SyncSnapshot(
        snapshot_id="snap-1",
        height=-1,
        state_hash="abc123",
    )

    assert not manager.synchronize(snapshot)

    assert manager.metrics.failures == 1