from influx.security.security_policy import (
    SecurityPolicy,
    SecurityPolicyManager,
)


def test_default_policy():

    manager = SecurityPolicyManager()

    assert (
        manager.validator_allowed(
            0
        )
        is True
    )


def test_validator_fault_limit():

    policy = SecurityPolicy(
        max_faults=2,
    )

    manager = SecurityPolicyManager(
        policy
    )

    assert (
        manager.validator_allowed(
            1
        )
        is True
    )

    assert (
        manager.validator_allowed(
            2
        )
        is False
    )


def test_attack_limit():

    manager = SecurityPolicyManager()

    assert (
        manager.attack_allowed(
            5
        )
        is True
    )

    assert (
        manager.attack_allowed(
            20
        )
        is False
    )