from __future__ import annotations

from .route import Route
from .route_table import RouteTable
from .route_validator import RouteValidator
from .routing_metrics import RoutingMetrics


class Routing:
    """
    Deterministic routing engine.
    """

    def __init__(self) -> None:

        self.table = RouteTable()
        self.validator = RouteValidator()
        self.metrics = RoutingMetrics()

    def add_route(
        self,
        route: Route,
    ) -> bool:

        self.metrics.record_attempt()

        if not self.validator.validate(route):
            return False

        if not self.table.add(route):
            return False

        self.metrics.record_created()
        return True

    def remove_route(
        self,
        route_id: str,
    ) -> bool:

        if not self.table.remove(route_id):
            return False

        self.metrics.record_removed()
        return True

    def lookup(
        self,
        route_id: str,
    ) -> Route | None:

        route = self.table.lookup(route_id)

        if route is None:
            self.metrics.record_failed_lookup()

        return route

    def best_route(
        self,
    ) -> Route | None:

        active = self.table.active_routes()

        if not active:
            return None

        return min(
            active,
            key=lambda route: (
                route.latency_score,
                route.hop_count,
                route.route_id,
            ),
        )

    def snapshot(
        self,
    ) -> dict[str, object]:

        return {
            "table": self.table.snapshot(),
            "metrics": self.metrics.snapshot(),
        }