from __future__ import annotations

from influx.runtime.services import RuntimeServices


class RuntimeLifecycle:
    """
    Controls runtime startup and shutdown.
    """

    def __init__(
        self,
        services: RuntimeServices,
    ) -> None:
        self.services = services
        self.started = False

    def start(self) -> None:
        """
        Start the runtime.
        """
        self.started = True

    def stop(self) -> None:
        """
        Stop the runtime.
        """
        self.started = False

    def restart(self) -> None:
        """
        Restart the runtime.
        """
        self.stop()
        self.start()