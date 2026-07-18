from influx.network.routing.message import Message
from influx.network.routing.route import Route
from influx.network.routing.routing_policy import RoutingPolicy


def create_route():
    return Route(
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


def test_valid_route():
    policy = RoutingPolicy()

    route = create_route()
    message = create_message()

    assert policy.validate(
        route,
        message,
    )


def test_inactive_route_fails():
    policy = RoutingPolicy()

    route = create_route()
    message = create_message()

    route.deactivate()

    assert not policy.validate(
        route,
        message,
    )


def test_excessive_hops_fail():
    policy = RoutingPolicy()

    route = create_route()
    message = create_message()

    route.hop_count = 999

    assert not policy.validate(
        route,
        message,
    )