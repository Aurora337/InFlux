from __future__ import annotations

from dataclasses import dataclass

from .message import Message
from .route import Route


@dataclass(slots=True)
class RoutingPolicy:
    """
    Determines whether a message may be routed.

    Policies are intentionally deterministic so every node
    reaches the same routing decision when presented with
    identical inputs.
    """

    max_hops: int = 16

    max_payload_size: int = 65536

    allow_broadcast: bool = True

    require_active_route: bool = True

    allow_loopback: bool = False


    def validate_route(
        self,
        route: Route,
    ) -> bool:
        """
        Validate a route.
        """

        if self.require_active_route and not route.active:
            return False

        if route.hop_count > self.max_hops:
            return False

        return True


    def validate_message(
        self,
        message: Message,
    ) -> bool:
        """
        Validate a message prior to routing.
        """

        if message.ttl <= 0:
            return False

        if message.payload_size() > self.max_payload_size:
            return False

        if (
            not self.allow_broadcast
            and message.destination == "*"
        ):
            return False

        if (
            not self.allow_loopback
            and message.source == message.destination
        ):
            return False

        return True


    def validate(
        self,
        route: Route,
        message: Message,
    ) -> bool:
        """
        Perform complete routing validation.
        """

        return (
            self.validate_route(route)
            and self.validate_message(message)
        )