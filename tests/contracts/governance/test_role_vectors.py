from influx.contracts.governance.role import GovernanceRole


def create_role():
    return GovernanceRole(
        role_id="role_001",
        principal="validator_001",
        role="admin",
    )


def test_role_creation():

    role = create_role()

    assert role.role == "admin"


def test_role_export():

    role = create_role()

    exported = role.to_dict()

    assert exported["principal"] == "validator_001"


def test_role_matches():

    role = create_role()

    assert role.has_role("admin")


def test_role_rejects_other_role():

    role = create_role()

    assert not role.has_role("operator")


def test_roles_are_deterministic():

    first = create_role()
    second = create_role()

    assert first.to_dict() == second.to_dict()


def test_role_is_immutable():

    role = create_role()

    try:
        role.role = "validator"
    except Exception:
        assert True
    else:
        assert False