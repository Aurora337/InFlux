from __future__ import annotations

from typing import Optional

from .message import Message
from .message_queue import MessageQueue
from .route import Route
from .route_table import RouteTable
from .routing_metrics import RoutingMetrics
from .routing_policy import RoutingPolicy


class Router:
    """
    Central deterministic routing coordinator.

    The Router coordinates route lookup, routing policy,
    queue management, and routing metrics. It intentionally
    contains no transport-specific logic, allowing it to be
    reused by future transport implementations.
    """

    def __init__(
        self,
        policy: Optional[RoutingPolicy] = None,
    ) -> None:

        self.route_table = RouteTable()

        self.queue = MessageQueue()

        self.policy = (
            policy
            if policy is not None
            else RoutingPolicy()
        )

        self.metrics = RoutingMetrics()


    def register_route(
        self,
        route: Route,
    ) -> None:
        """
        Register a route.
        """

        self.route_table.add(route)


    def remove_route(
        self,
        destination: str,
    ) -> None:
        """
        Remove a route.
        """

        self.route_table.remove(destination)


    def lookup(
        self,
        destination: str,
    ) -> Optional[Route]:
        """
        Find a route.
        """

        route = self.route_table.lookup(
            destination
        )

        self.metrics.record_lookup(
            route is not None
        )

        return route


    def enqueue(
        self,
        message: Message,
    ) -> None:
        """
        Queue a message.
        """

        self.queue.enqueue(
            message
        )


    def next_message(
        self,
    ) -> Optional[Message]:
        """
        Retrieve the next queued message.
        """

        return self.queue.dequeue()


    def route(
        self,
        message: Message,
    ) -> bool:
        """
        Attempt to route a message.

        Returns
        -------
        bool
            True if successfully routed.
        """

        route = self.lookup(
            message.destination
        )

        if route is None:

            self.metrics.record_failure()

            return False


        if not self.policy.validate(
            route,
            message,
        ):

            self.metrics.record_failure()

            return False


        if not message.decrement_ttl():

            self.metrics.record_ttl_expired()

            self.metrics.record_drop()

            message.mark_dropped()

            return False


        self.metrics.record_route(
            message.payload_size()
        )

        self.enqueue(
            message
        )

        return True


    def deliver(self) -> Optional[Message]:
        """
        Deliver the next queued message.
        """

        message = self.next_message()

        if message is None:

            return None


        message.mark_delivered()

        self.metrics.record_delivery()

        return message


    def broadcast(
        self,
        message: Message,
    ) -> bool:
        """
        Broadcast a message.

        The caller is responsible for creating
        per-destination copies if necessary.
        """

        message.destination = "*"

        self.metrics.record_broadcast()

        self.enqueue(
            message
        )

        return True


    def snapshot(self) -> dict:
        """
        Deterministic router snapshot.
        """

        return {
            "routes": self.route_table.snapshot(),
            "queue": self.queue.snapshot(),
            "metrics": self.metrics.snapshot(),
        }