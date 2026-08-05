from __future__ import annotations

from dataclasses import dataclass

from .dispatcher import RuntimeDispatcher
from .executor import RuntimeExecutor
from .lifecycle import RuntimeLifecycle
from .monitor import RuntimeMonitor
from .queue import RuntimeQueue
from .scheduler import RuntimeScheduler


@dataclass(slots=True)
class RuntimeCoordinator:
    """
    Coordinates the runtime execution pipeline.

    Connects:
    lifecycle
    queue
    scheduler
    dispatcher
    executor
    monitoring
    """

    lifecycle: RuntimeLifecycle
    queue: RuntimeQueue
    executor: RuntimeExecutor
    scheduler: RuntimeScheduler
    dispatcher: RuntimeDispatcher
    monitor: RuntimeMonitor

    def start(self) -> None:
        """
        Start runtime services.
        """

        self.lifecycle.start()
        self.monitor.start()

    def stop(self) -> None:
        """
        Stop runtime services.
        """

        self.monitor.stop()
        self.lifecycle.stop()

    def process(
        self,
    ) -> int:
        """
        Process queued runtime tasks.

        Returns number of processed tasks.
        """

        tasks = self.scheduler.next_batch()

        processed = 0

        for task in tasks:
            receipt = self.dispatcher.dispatch(
                task,
                self.executor,
            )

            self.monitor.record(
                receipt,
            )

            processed += 1

        return processed