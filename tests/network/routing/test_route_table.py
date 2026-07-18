from influx.network.routing.route import Route
from influx.network.routing.route_table import RouteTable


def create_route(
    destination="node-b",
):
    return Route(
        destination=destination,
        cost=1,
    )


def test_add_route():
    table = RouteTable()

    route = create_route()

    result = table.add(route)

    assert result
    assert table.lookup(route.route_id) == route


def test_duplicate_route():
    table = RouteTable()

    route = create_route()

    table.add(route)

    result = table.add(route)

    assert not result


def test_lookup_route():
    table = RouteTable()

    route = create_route()

    table.add(route)

    result = table.lookup(
        route.route_id
    )

    assert result == route


def test_remove_route():
    table = RouteTable()

    route = create_route()

    table.add(route)

    result = table.remove(
        route.route_id
    )

    assert result
    assert table.lookup(route.route_id) is None


def test_snapshot():
    table = RouteTable()

    route = create_route()

    table.add(route)

    snapshot = table.snapshot()

    assert route.route_id in snapshot