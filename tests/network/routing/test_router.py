from influx.network.routing.message import Message
from influx.network.routing.route import Route
from influx.network.routing.router import Router


def create_route():
    return Route(
        route_id="node-b",
        destination="node-b",
        cost=1,
    )


def create_message():
    return Message(
        source="node-a",
        destination="node-b",
        payload={
            "event": "test",
        },
    )


def test_register_route():

    router = Router()

    route = create_route()

    result = router.register_route(
        route
    )

    assert result is None


def test_lookup():

    router = Router()

    route = create_route()

    router.register_route(
        route
    )

    result = router.lookup(
        route.route_id
    )

    assert result == route


def test_route_message():

    router = Router()

    route = create_route()

    router.register_route(
        route
    )

    message = create_message()

    result = router.route(
        message
    )

    assert result


def test_deliver():

    router = Router()

    route = create_route()

    router.register_route(
        route
    )

    message = create_message()

    router.route(
        message
    )

    result = router.deliver()

    assert result == message


def test_broadcast():

    router = Router()

    message = create_message()

    result = router.broadcast(
        message
    )

    assert result


def test_snapshot():

    router = Router()

    snapshot = router.snapshot()

    assert "routes" in snapshot
    assert "queue" in snapshot
    assert "metrics" in snapshot