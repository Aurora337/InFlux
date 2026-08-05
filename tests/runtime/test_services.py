from influx.runtime.services import RuntimeServices


class DummyService:
    pass


def test_register_service() -> None:
    services = RuntimeServices()

    network = DummyService()

    services.register("network", network)

    assert services.get("network") is network


def test_missing_service_returns_none() -> None:
    services = RuntimeServices()

    assert services.get("missing") is None


def test_contains_service() -> None:
    services = RuntimeServices()

    services.register("ledger", DummyService())

    assert services.has("ledger")
    assert not services.has("rpc")


def test_registered_service_names() -> None:
    services = RuntimeServices()

    services.register("network", DummyService())
    services.register("ledger", DummyService())

    names = services.names()

    assert "network" in names
    assert "ledger" in names