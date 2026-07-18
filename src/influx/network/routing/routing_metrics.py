from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RoutingMetrics:
    """
    Tracks deterministic routing activity.
    """

    routes_created: int = 0
    routes_removed: int = 0
    routing_attempts: int = 0
    failed_lookups: int = 0

    route_lookups: int = 0
    routing_failures: int = 0
    ttl_expired: int = 0
    packets_dropped: int = 0
    packets_routed: int = 0
    packets_delivered: int = 0
    broadcasts: int = 0

    def record_attempt(self) -> None:
        self.routing_attempts += 1

    def record_created(self) -> None:
        self.routes_created += 1

    def record_removed(self) -> None:
        self.routes_removed += 1

    def record_failed_lookup(self) -> None:
        self.failed_lookups += 1

    def record_lookup(
        self,
        found: bool,
    ) -> None:
        """
        Record a route lookup.
        """

        _ = found

        self.route_lookups += 1

    def record_failure(self) -> None:
        self.routing_failures += 1

    def record_ttl_expired(self) -> None:
        self.ttl_expired += 1

    def record_drop(self) -> None:
        self.packets_dropped += 1

    def record_route(
        self,
        payload_size: int,
    ) -> None:
        """
        Record a routed packet.
        """

        _ = payload_size

        self.packets_routed += 1

    def record_delivery(self) -> None:
        self.packets_delivered += 1

    def record_broadcast(self) -> None:
        self.broadcasts += 1

    def snapshot(self) -> dict[str, int]:
        return {
            "routes_created": self.routes_created,
            "routes_removed": self.routes_removed,
            "routing_attempts": self.routing_attempts,
            "failed_lookups": self.failed_lookups,
            "route_lookups": self.route_lookups,
            "routing_failures": self.routing_failures,
            "ttl_expired": self.ttl_expired,
            "packets_dropped": self.packets_dropped,
            "packets_routed": self.packets_routed,
            "packets_delivered": self.packets_delivered,
            "broadcasts": self.broadcasts,
        }