from influx.governance.governance_metrics import (
    GovernanceMetrics,
)


def test_governance_metrics():

    metrics = GovernanceMetrics()

    metrics.record_proposal()

    metrics.record_vote()

    metrics.record_approval()

    metrics.record_rejection()

    metrics.record_upgrade()

    assert (
        metrics.proposals_created
        == 1
    )

    assert (
        metrics.votes_cast
        == 1
    )

    assert (
        metrics.proposals_approved
        == 1
    )

    assert (
        metrics.proposals_rejected
        == 1
    )

    assert (
        metrics.upgrades_activated
        == 1
    )


def test_governance_snapshot():

    metrics = GovernanceMetrics()

    snapshot = metrics.snapshot()

    assert (
        "proposals_created"
        in snapshot
    )

    assert (
        "votes_cast"
        in snapshot
    )

    assert (
        "upgrades_activated"
        in snapshot
    )