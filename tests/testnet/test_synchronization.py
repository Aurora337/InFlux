from influx.testnet.synchronization import (
    ClusterStateExchange,
    SynchronizationSession,
    SynchronizationResult,
)


def test_cluster_state_exchange_digest_deterministic() -> None:
    exchange_one = ClusterStateExchange(
        cluster_id="cluster-a",
        state_snapshot={
            "members": ["node-1"],
            "ledger_height": 10,
        },
        cluster_hash="abc123",
    )

    exchange_two = ClusterStateExchange(
        cluster_id="cluster-a",
        state_snapshot={
            "ledger_height": 10,
            "members": ["node-1"],
        },
        cluster_hash="abc123",
    )

    assert (
        exchange_one.exchange_digest()
        ==
        exchange_two.exchange_digest()
    )


def test_cluster_state_exchange_rejects_empty_cluster_id() -> None:
    try:
        ClusterStateExchange(
            cluster_id="",
            state_snapshot={},
            cluster_hash="hash",
        )
    except ValueError as exc:
        assert str(exc) == "cluster_id must be non-empty"
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_synchronization_session_converges() -> None:
    session = SynchronizationSession(
        "cluster-a",
        "cluster-b",
    )

    session.exchange_state(
        "cluster-a",
        {
            "members": ["node-1"],
            "height": 20,
        },
        "hash-001",
    )

    session.exchange_state(
        "cluster-b",
        {
            "members": ["node-1"],
            "height": 20,
        },
        "hash-001",
    )

    assert session.synchronize() is True

    result = session.verify_convergence()

    assert result["converged"] is True
    assert result["hashes_match"] is True
    assert result["session_complete"] is True
    assert result["convergence_hash"] == "hash-001"


def test_synchronization_session_detects_mismatch() -> None:
    session = SynchronizationSession(
        "cluster-a",
        "cluster-b",
    )

    session.exchange_state(
        "cluster-a",
        {},
        "hash-a",
    )

    session.exchange_state(
        "cluster-b",
        {},
        "hash-b",
    )

    assert session.synchronize() is False

    result = session.verify_convergence()

    assert result["converged"] is False
    assert result["hashes_match"] is False


def test_session_digest_is_deterministic() -> None:
    session_one = SynchronizationSession(
        "cluster-a",
        "cluster-b",
    )

    session_two = SynchronizationSession(
        "cluster-a",
        "cluster-b",
    )

    assert (
        session_one.session_digest()
        ==
        session_two.session_digest()
    )


def test_synchronization_result() -> None:
    session = SynchronizationSession(
        "cluster-a",
        "cluster-b",
    )

    session.exchange_state(
        "cluster-a",
        {},
        "shared-hash",
    )

    session.exchange_state(
        "cluster-b",
        {},
        "shared-hash",
    )

    session.synchronize()

    result = SynchronizationResult()

    result.add_session_result(
        session,
    )

    assert result.all_converged() is True
    assert result.convergence_hash_match() is True

    summary = result.result_summary()

    assert summary["sessions_completed"] == 1
    assert summary["all_converged"] is True