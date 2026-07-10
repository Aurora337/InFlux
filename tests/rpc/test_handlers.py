from influx.rpc.handlers import (
    RPCHandlerRegistry,
)


def test_register_handler():

    registry = RPCHandlerRegistry()

    registry.register(
        "ping",
        lambda: "pong",
    )

    assert (
        registry.exists(
            "ping"
        )
        is True
    )


def test_get_handler():

    registry = RPCHandlerRegistry()

    registry.register(
        "ping",
        lambda: "pong",
    )

    handler = registry.get(
        "ping"
    )

    assert (
        handler()
        == "pong"
    )


def test_unregister_handler():

    registry = RPCHandlerRegistry()

    registry.register(
        "ping",
        lambda: "pong",
    )

    removed = registry.unregister(
        "ping"
    )

    assert removed is True

    assert (
        registry.exists(
            "ping"
        )
        is False
    )


def test_registered_methods():

    registry = RPCHandlerRegistry()

    registry.register(
        "ping",
        lambda: "pong",
    )

    registry.register(
        "status",
        lambda: "ok",
    )

    methods = registry.methods()

    assert (
        "ping"
        in methods
    )

    assert (
        "status"
        in methods
    )