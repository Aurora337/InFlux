from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeState:
    """
    Current runtime state.
    """

    started: bool = False
    stopping: bool = False
    healthy: bool = True

    def start(self) -> None:
        self.started = True
        self.stopping = False

    def stop(self) -> None:
        self.started = False
        self.stopping = True

    def mark_healthy(self) -> None:
        self.healthy = True

    def mark_unhealthy(self) -> None:
        self.healthy = False

    def set(
        self,
        key: str,
        value: bool,
    ) -> None:
        """
        Update runtime state field deterministically.
        """

        if not hasattr(self, key):
            raise AttributeError(
                f"unknown runtime state field: {key}"
            )

        setattr(
            self,
            key,
            value,
        )