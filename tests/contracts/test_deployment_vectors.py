from influx.contracts.deployment import ContractDeployment
from influx.contracts.persistence import ContractPersistence
from influx.contracts.registry import ContractRegistry


def create_deployment():
    return ContractDeployment(
        persistence=ContractPersistence(),
        registry=ContractRegistry(),
    )


def create_metadata():
    return {
        "owner": "validator_001",
        "version": "1.0.0",
        "code_hash": "abc123",
    }


def test_deploy_contract():
    deployment = create_deployment()

    deployment.deploy(
        "contract_a",
        create_metadata(),
    )

    assert deployment.is_deployed("contract_a")


def test_duplicate_deploy_fails():
    deployment = create_deployment()

    deployment.deploy(
        "contract_a",
        create_metadata(),
    )

    try:
        deployment.deploy(
            "contract_a",
            create_metadata(),
        )
    except ValueError:
        assert True
    else:
        assert False


def test_undeploy_contract():
    deployment = create_deployment()

    deployment.deploy(
        "contract_a",
        create_metadata(),
    )

    deployment.undeploy("contract_a")

    assert not deployment.is_deployed("contract_a")


def test_registry_and_persistence_match():
    deployment = create_deployment()

    deployment.deploy(
        "contract_a",
        create_metadata(),
    )

    assert deployment.registry.exists("contract_a")
    assert deployment.persistence.exists("contract_a")


def test_multiple_deployments():
    deployment = create_deployment()

    deployment.deploy("a", create_metadata())
    deployment.deploy("b", create_metadata())

    assert deployment.registry.count() == 2


def test_deployment_is_deterministic():
    first = create_deployment()
    second = create_deployment()

    first.deploy("contract", create_metadata())
    second.deploy("contract", create_metadata())

    assert (
        first.registry.contract_ids()
        == second.registry.contract_ids()
    )