from influx.contracts.governance.authority import GovernanceAuthority
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


def test_authorized_action():

    authority = GovernanceAuthority()

    assert authority.authorize(
        create_policy(),
        create_role(),
        "upgrade_contract",
    )


def test_wrong_role_rejected():

    authority = GovernanceAuthority()

    assert not authority.authorize(
        create_policy(),
        create_role("operator"),
        "upgrade_contract",
    )


def test_wrong_action_rejected():

    authority = GovernanceAuthority()

    assert not authority.authorize(
        create_policy(),
        create_role(),
        "deploy_contract",
    )


def test_authorization_is_deterministic():

    authority = GovernanceAuthority()

    first = authority.authorize(
        create_policy(),
        create_role(),
        "upgrade_contract",
    )

    second = authority.authorize(
        create_policy(),
        create_role(),
        "upgrade_contract",
    )

    assert first == second


def test_multiple_roles():

    authority = GovernanceAuthority()

    assert authority.authorize(
        create_policy(),
        create_role("admin"),
        "upgrade_contract",
    )


def test_non_matching_role():

    authority = GovernanceAuthority()

    assert not authority.authorize(
        create_policy(),
        create_role("guest"),
        "upgrade_contract",
    )