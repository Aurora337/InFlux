from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RoutingMetrics:
    """
    Deterministic routing statistics.

    These metrics are intended for observability,
    replay analysis, benchmarking, and future
    adaptive routing algorithms.
    """

    messages_routed: int = 0

    messages_delivered: int = 0

    messages_dropped: int = 0

    routing_failures: int = 0

    broadcasts: int = 0

    route_lookups: int = 0

    route_misses: int = 0

    ttl_expired: int = 0

    bytes_routed: int = 0


    def record_route(
        self,
        bytes_sent: int,
    ) -> None:
        """
        Record a routed message.
        """

        self.messages_routed += 1
        self.bytes_routed += bytes_sent


    def record_delivery(self) -> None:
        """
        Record successful delivery.
        """

        self.messages_delivered += 1


    def record_drop(self) -> None:
        """
        Record a dropped message.
        """

        self.messages_dropped += 1


    def record_failure(self) -> None:
        """
        Record a routing failure.
        """

        self.routing_failures += 1


    def record_broadcast(self) -> None:
        """
        Record a broadcast event.
        """

        self.broadcasts += 1


    def record_lookup(
        self,
        found: bool,
    ) -> None:
        """
        Record route lookup activity.
        """

        self.route_lookups += 1

        if not found:
            self.route_misses += 1


    def record_ttl_expired(self) -> None:
        """
        Record TTL expiration.
        """

        self.ttl_expired += 1


    @property
    def delivery_rate(self) -> float:
        """
        Successful delivery percentage.
        """

        if self.messages_routed == 0:
            return 0.0

        return (
            self.messages_delivered
            / self.messages_routed
        )


    @property
    def lookup_success_rate(self) -> float:
        """
        Successful route lookup percentage.
        """

        if self.route_lookups == 0:
            return 0.0

        return (
            (
                self.route_lookups
                - self.route_misses
            )
            / self.route_lookups
        )


    def snapshot(self) -> dict[str, int | float]:
        """
        Produce a deterministic metrics snapshot.
        """

        return {
            "messages_routed": self.messages_routed,
            "messages_delivered": self.messages_delivered,
            "messages_dropped": self.messages_dropped,
            "routing_failures": self.routing_failures,
            "broadcasts": self.broadcasts,
            "route_lookups": self.route_lookups,
            "route_misses": self.route_misses,
            "ttl_expired": self.ttl_expired,
            "bytes_routed": self.bytes_routed,
            "delivery_rate": self.delivery_rate,
            "lookup_success_rate": self.lookup_success_rate,
        }