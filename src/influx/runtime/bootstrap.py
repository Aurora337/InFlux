from __future__ import annotations

from influx.runtime.config import RuntimeConfig
from influx.runtime.services import RuntimeServices


def bootstrap_runtime(
    config: RuntimeConfig | None = None,
) -> RuntimeServices:
    """
    Build the runtime service container.

    This initializes the runtime dependency graph but does
    not start any long-running services.
    """

    runtime_config = config or RuntimeConfig()

    services = RuntimeServices()

    services.register(
        "config",
        runtime_config,
    )

    return services