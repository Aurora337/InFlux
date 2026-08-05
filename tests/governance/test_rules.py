from influx.governance.governance_rules import (
    GovernanceRules,
    GovernanceRuleEngine,
)


def test_default_rules():

    engine = GovernanceRuleEngine()

    assert (
        engine.valid_proposal(
            True
        )
        is True
    )


def test_inactive_proposal_blocked():

    engine = GovernanceRuleEngine()

    assert (
        engine.valid_proposal(
            False
        )
        is False
    )


def test_vote_requirement():

    rules = GovernanceRules(
        minimum_votes=3,
    )

    engine = GovernanceRuleEngine(
        rules,
    )

    assert (
        engine.valid_votes(
            3
        )
        is True
    )

    assert (
        engine.valid_votes(
            2
        )
        is False
    )


def test_disabled_active_requirement():

    rules = GovernanceRules(
        require_active_proposal=False,
    )

    engine = GovernanceRuleEngine(
        rules,
    )

    assert (
        engine.valid_proposal(
            False
        )
        is True
    )