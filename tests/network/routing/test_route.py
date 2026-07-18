from influx.network.routing.route import Route


def create_route():
    return Route(
        destination="node-b",
        cost=1,
    )


def test_route_creation():
    route = create_route()

    assert route.destination == "node-b"
    assert route.cost == 1


def test_route_validation():
    route = create_route()

    assert route.validate()


def test_route_snapshot():
    route = create_route()

    snapshot = route.snapshot()

    assert snapshot["destination"] == "node-b"
    assert "route_id" in snapshot