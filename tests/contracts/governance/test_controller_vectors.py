from influx.contracts.governance.controller import GovernanceController
from influx.contracts.governance.policy import GovernancePolicy
from influx.contracts.governance.role import GovernanceRole


def create_policy():
    return GovernancePolicy(
        policy_id="policy_001",
        action="upgrade_contract",
        required_role="admin",
        description="Upgrade policy",
    )


def create_role(role="admin"):
    return GovernanceRole(
        role_id="role_001",
        principal="validator_001",
        role=role,
    )


def test_controller_authorizes():

    controller = GovernanceController()

    assert controller.authorize(
        create_policy(),
        create_role(),
        "upgrade_contract",
    )


def test_controller_rejects_wrong_role():

    controller = GovernanceController()

    assert not controller.authorize(
        create_policy(),
        create_role("guest"),
        "upgrade_contract",
    )


def test_controller_rejects_wrong_action():

    controller = GovernanceController()

    assert not controller.authorize(
        create_policy(),
        create_role(),
        "deploy_contract",
    )


def test_controller_is_deterministic():

    controller = GovernanceController()

    first = controller.authorize(
        create_policy(),
        create_role(),
        "upgrade_contract",
    )

    second = controller.authorize(
        create_policy(),
        create_role(),
        "upgrade_contract",
    )

    assert first == second


def test_multiple_authorizations():

    controller = GovernanceController()

    assert controller.authorize(
        create_policy(),
        create_role("admin"),
        "upgrade_contract",
    )


def test_guest_cannot_upgrade():

    controller = GovernanceController()

    assert not controller.authorize(
        create_policy(),
        create_role("guest"),
        "upgrade_contract",
    )
    