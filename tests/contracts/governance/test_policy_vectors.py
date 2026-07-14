from influx.contracts.governance.policy import GovernancePolicy


def create_policy():
    return GovernancePolicy(
        policy_id="policy_001",
        action="upgrade_contract",
        required_role="admin",
        description="Only administrators may upgrade contracts.",
    )


def test_policy_creation():

    policy = create_policy()

    assert policy.policy_id == "policy_001"


def test_policy_export():

    policy = create_policy()

    exported = policy.to_dict()

    assert exported["action"] == "upgrade_contract"
    assert exported["required_role"] == "admin"


def test_policy_matches_action():

    policy = create_policy()

    assert policy.matches("upgrade_contract")


def test_policy_rejects_other_action():

    policy = create_policy()

    assert not policy.matches("deploy_contract")


def test_policy_is_deterministic():

    first = create_policy()
    second = create_policy()

    assert first.to_dict() == second.to_dict()


def test_policy_is_immutable():

    policy = create_policy()

    try:
        policy.required_role = "validator"
    except Exception:
        assert True
    else:
        assert False