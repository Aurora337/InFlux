from influx.network.routing.routing_metrics import RoutingMetrics


def test_initial_metrics():
    metrics = RoutingMetrics()

    snapshot = metrics.snapshot()

    assert snapshot


def test_record_lookup():

    metrics = RoutingMetrics()

    metrics.record_lookup(
        True
    )

    snapshot = metrics.snapshot()

    assert snapshot


def test_record_route():

    metrics = RoutingMetrics()

    metrics.record_route(
        100
    )

    snapshot = metrics.snapshot()

    assert snapshot


def test_record_failure():

    metrics = RoutingMetrics()

    metrics.record_failure()

    snapshot = metrics.snapshot()

    assert snapshot