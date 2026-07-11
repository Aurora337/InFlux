from influx.testnet.deployment import (
    TestnetDeployment,
)

from influx.testnet.network import (
    TestnetNetwork,
)


def test_deploy_node() -> None:
    network = TestnetNetwork()

    deployment = TestnetDeployment(
        network,
    )

    node = deployment.deploy_node(
        "node-1",
    )

    assert node.online is True
    assert network.node_count() == 1


def test_shutdown() -> None:
    network = TestnetNetwork()

    deployment = TestnetDeployment(
        network,
    )

    deployment.deploy_node(
        "node-1",
    )

    deployment.shutdown()

    assert network.online_nodes() == []