from influx.node_runtime.health import NodeHealth


def test_health_activation() -> None:
    health = NodeHealth()

    health.activate()

    assert health.online is True
    assert health.healthy is True


def test_health_shutdown() -> None:
    health = NodeHealth(
        online=True,
        healthy=True,
    )

    health.deactivate()

    assert health.online is False
    assert health.healthy is False


def test_sync_state() -> None:
    health = NodeHealth()

    health.mark_synced()

    assert health.synced is True