from __future__ import annotations

import signal
from collections.abc import Callable


class RuntimeSignalHandler:
    """
    Registers operating system signal handlers.
    """

    def __init__(
        self,
        shutdown: Callable[[], None],
    ) -> None:
        self.shutdown = shutdown

    def register(self) -> None:
        signal.signal(signal.SIGINT, self._handle)

        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._handle)

    def _handle(self, signum: int, frame: object) -> None:
        self.shutdown()