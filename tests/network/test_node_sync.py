from influx.network.node.node_sync import NodeSync


def test_sync_start() -> None:
    sync = NodeSync()

    sync.start(100)

    assert sync.target_height == 100
    assert not sync.is_synced()


def test_sync_update() -> None:
    sync = NodeSync()

    sync.start(100)

    sync.update(50)

    assert sync.current_height == 50
    assert not sync.is_synced()


def test_sync_complete() -> None:
    sync = NodeSync()

    sync.start(100)

    sync.update(100)

    assert sync.is_synced()


def test_sync_reset() -> None:
    sync = NodeSync()

    sync.start(100)
    sync.update(100)

    sync.reset()

    assert not sync.is_synced()
    assert sync.current_height == 0