from __future__ import annotations

from .route import Route


class RouteTable:
    """
    Deterministic route registry.
    """

    def __init__(
        self,
    ) -> None:

        self.routes: dict[str, Route] = {}


    def add(
        self,
        route: Route,
    ) -> bool:
        """
        Add route indexed by destination.
        """

        if route.destination in self.routes:
            return False

        self.routes[
            route.destination
        ] = route

        return True


    def remove(
        self,
        destination: str,
    ) -> bool:
        """
        Remove route by destination.
        """

        if destination not in self.routes:
            return False

        del self.routes[
            destination
        ]

        return True


    def lookup(
        self,
        destination: str,
    ) -> Route | None:
        """
        Lookup route by destination.
        """

        return self.routes.get(
            destination
        )


    def active_routes(
        self,
    ) -> list[Route]:
        """
        Return active routes.
        """

        return [
            route
            for route in self.routes.values()
            if route.active
        ]


    def count(
        self,
    ) -> int:
        """
        Return route count.
        """

        return len(
            self.routes
        )


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic snapshot.
        """

        return {
            destination: route.snapshot()
            for destination, route in self.routes.items()
        }