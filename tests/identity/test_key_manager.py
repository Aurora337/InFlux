from influx.identity.key_manager import (
    KeyManager,
    KeyPair,
)


def test_register_key():

    manager = KeyManager()

    pair = KeyPair(
        public_key="public",
        private_key="private",
    )

    manager.register(
        "node-1",
        pair,
    )

    assert (
        manager.exists(
            "node-1"
        )
        is True
    )


def test_get_key():

    manager = KeyManager()

    pair = KeyPair(
        public_key="public",
        private_key="private",
    )

    manager.register(
        "node-1",
        pair,
    )

    result = manager.get(
        "node-1"
    )

    assert result == pair


def test_remove_key():

    manager = KeyManager()

    manager.register(
        "node-1",
        KeyPair(
            public_key="public",
            private_key="private",
        ),
    )

    removed = manager.remove(
        "node-1"
    )

    assert (
        removed
        is True
    )

    assert (
        manager.exists(
            "node-1"
        )
        is False
    )


def test_missing_key():

    manager = KeyManager()

    assert (
        manager.get(
            "missing"
        )
        is None
    )