from influx.identity.rotation import (
    KeyRotation,
    RotationManager,
)


def test_key_rotation():

    manager = RotationManager()

    rotation = manager.rotate(
        identity_id="node-1",
        old_key="old",
        new_key="new",
        timestamp=100,
    )

    assert isinstance(
        rotation,
        KeyRotation,
    )

    assert (
        rotation.new_key
        == "new"
    )


def test_rotation_history():

    manager = RotationManager()

    manager.rotate(
        identity_id="node-1",
        old_key="old",
        new_key="new",
        timestamp=100,
    )

    history = manager.history()

    assert len(history) == 1

    assert (
        history[0].identity_id
        == "node-1"
    )


def test_history_returns_copy():

    manager = RotationManager()

    manager.rotate(
        identity_id="node-1",
        old_key="old",
        new_key="new",
        timestamp=100,
    )

    first = manager.history()
    second = manager.history()

    assert first is not second

    first.clear()

    assert len(
        manager.history()
    ) == 1