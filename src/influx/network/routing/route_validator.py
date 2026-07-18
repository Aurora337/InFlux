from __future__ import annotations

from .route import Route


class RouteValidator:
    """
    Validates routes.
    """

    def validate(
        self,
        route: Route,
    ) -> bool:

        try:
            route.validate()
        except ValueError:
            return False

        return True