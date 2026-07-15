from influx.runtime.bootstrap import bootstrap_runtime
from influx.runtime.config import RuntimeConfig
from influx.runtime.services import RuntimeServices


def test_bootstrap_returns_service_container() -> None:
    services = bootstrap_runtime()

    assert isinstance(services, RuntimeServices)


def test_bootstrap_registers_configuration() -> None:
    services = bootstrap_runtime()

    config = services.get("config")

    assert isinstance(config, RuntimeConfig)


def test_bootstrap_accepts_custom_configuration() -> None:
    config = RuntimeConfig(
        node_name="validator-01",
        port=7000,
    )

    services = bootstrap_runtime(config)

    runtime_config = services.get("config")

    assert runtime_config is config