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
        Add route.
        """

        if route.route_id in self.routes:
            return False

        self.routes[
            route.route_id
        ] = route

        return True


    def remove(
        self,
        route_id: str,
    ) -> bool:
        """
        Remove route.
        """

        if route_id not in self.routes:
            return False

        del self.routes[
            route_id
        ]

        return True


    def lookup(
        self,
        route_id: str,
    ) -> Route | None:
        """
        Lookup route.
        """

        return self.routes.get(
            route_id
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

        return len(self.routes)


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Return deterministic snapshot.
        """

        return {
            route_id: route.snapshot()
            for route_id, route in self.routes.items()
        }