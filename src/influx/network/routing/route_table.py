from __future__ import annotations

from typing import Dict, List, Optional

from .route import Route


class RouteTable:
    """
    Deterministic routing table.

    Maintains known routes indexed by destination.
    """

    def __init__(self) -> None:
        self._routes: Dict[str, Route] = {}


    def add(self, route: Route) -> None:
        """
        Add or replace a route.
        """

        self._routes[route.destination] = route


    def remove(
        self,
        destination: str,
    ) -> None:
        """
        Remove a destination.
        """

        self._routes.pop(
            destination,
            None,
        )


    def lookup(
        self,
        destination: str,
    ) -> Optional[Route]:
        """
        Retrieve a route.
        """

        return self._routes.get(
            destination
        )


    def exists(
        self,
        destination: str,
    ) -> bool:
        """
        Determine whether a route exists.
        """

        return destination in self._routes


    def update(
        self,
        route: Route,
    ) -> None:
        """
        Replace an existing route.
        """

        self._routes[
            route.destination
        ] = route

        route.touch()


    def active(self) -> List[Route]:
        """
        Return active routes.
        """

        return [
            route
            for route in self._routes.values()
            if route.active
        ]


    def clear(self) -> None:
        """
        Remove every route.
        """

        self._routes.clear()


    def snapshot(self) -> dict:
        """
        Deterministic routing snapshot.
        """

        return {
            destination: route.snapshot()
            for destination, route
            in self._routes.items()
        }