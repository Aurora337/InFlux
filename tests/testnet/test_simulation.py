from influx.testnet.simulation import (
    TestnetSimulation,
)

from influx.testnet.network import (
    TestnetNetwork,
)


def test_simulation_creation() -> None:
    network = TestnetNetwork()

    simulation = TestnetSimulation(
        network,
    )

    assert simulation.node_count() == 0
    assert simulation.event_count() == 0


def test_record_event() -> None:
    network = TestnetNetwork()

    simulation = TestnetSimulation(
        network,
    )

    simulation.record_event(
        "node_joined",
    )

    assert simulation.event_count() == 1