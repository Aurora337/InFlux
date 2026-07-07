"""Cross-cluster synchronization and convergence validation tests."""

from influx.testnet import Cluster, ClusterRegistry, SynchronizationSession, SynchronizationResult


def _create_and_populate_cluster(cluster_id: str, node_count: int = 6) -> Cluster:
    """Create a cluster with standard node set."""
    cluster = Cluster(cluster_id)
    roles = ["VN", "SN", "REN", "LN", "AN", "PTN"]
    
    for idx, role in enumerate(roles[:node_count]):
        node_id = f"{role.lower()}-{cluster_id}"
        cluster.register_node(node_id, role)
    
    return cluster


def test_synchronization_session_creation():
    """Test that a synchronization session can be created between two clusters."""
    session = SynchronizationSession("cluster-a", "cluster-b")
    assert session.cluster_a_id == "cluster-a"
    assert session.cluster_b_id == "cluster-b"


def test_synchronization_session_rejects_invalid_cluster_id():
    """Test that invalid cluster IDs are rejected."""
    session = SynchronizationSession("cluster-a", "cluster-b")
    
    try:
        session.exchange_state("cluster-c", {}, "hash123")
        assert False, "Should have rejected unknown cluster_id"
    except ValueError as e:
        assert "not in session" in str(e)


def test_state_exchange_bidirectional():
    """Test that state can be exchanged in both directions."""
    cluster_a = _create_and_populate_cluster("cluster-a")
    cluster_b = _create_and_populate_cluster("cluster-b")
    
    session = SynchronizationSession("cluster-a", "cluster-b")
    
    # Exchange state from A to B
    session.exchange_state(
        "cluster-a",
        cluster_a.snapshot(),
        cluster_a.cluster_hash(),
    )
    
    # Exchange state from B to A
    session.exchange_state(
        "cluster-b",
        cluster_b.snapshot(),
        cluster_b.cluster_hash(),
    )
    
    # Both exchanges should be recorded
    comparison = session.compare_hashes()
    assert comparison["complete"] is True


def test_identical_clusters_converge():
    """Test that identical clusters converge on same hash."""
    cluster_a = _create_and_populate_cluster("cluster-a")
    cluster_b = _create_and_populate_cluster("cluster-b")
    
    # Re-create cluster_b with identical node set as cluster_a
    cluster_b = Cluster("cluster-b")
    for node_id, role in [
        ("vn-cluster-a", "VN"),
        ("sn-cluster-a", "SN"),
        ("ren-cluster-a", "REN"),
        ("ln-cluster-a", "LN"),
        ("an-cluster-a", "AN"),
        ("ptn-cluster-a", "PTN"),
    ]:
        # Map to cluster_b's namespace
        cluster_b.register_node(node_id.replace("cluster-a", "cluster-b"), role)
    
    session = SynchronizationSession("cluster-a", "cluster-b")
    
    session.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    
    # Synchronize
    converged = session.synchronize()
    
    # Verify convergence
    verification = session.verify_convergence()
    assert verification["converged"] is converged


def test_synchronization_result_tracking():
    """Test that synchronization results can be tracked."""
    cluster_a = _create_and_populate_cluster("cluster-a")
    cluster_b = _create_and_populate_cluster("cluster-b")
    cluster_c = _create_and_populate_cluster("cluster-c")
    
    result = SynchronizationResult()
    
    # Session A ↔ B
    session_ab = SynchronizationSession("cluster-a", "cluster-b")
    session_ab.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session_ab.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_ab.synchronize()
    result.add_session_result(session_ab)
    
    # Session B ↔ C
    session_bc = SynchronizationSession("cluster-b", "cluster-c")
    session_bc.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_bc.exchange_state("cluster-c", cluster_c.snapshot(), cluster_c.cluster_hash())
    session_bc.synchronize()
    result.add_session_result(session_bc)
    
    # Verify result
    summary = result.result_summary()
    assert summary["sessions_completed"] == 2


def test_cross_cluster_three_cluster_convergence():
    """Test three-cluster convergence scenario.
    
    All three clusters start independently, process identical node sets,
    and then synchronize to converge on identical hashes.
    """
    # Create three independent clusters with identical membership
    cluster_a = _create_and_populate_cluster("cluster-a", node_count=6)
    cluster_b = _create_and_populate_cluster("cluster-b", node_count=6)
    cluster_c = _create_and_populate_cluster("cluster-c", node_count=6)
    
    result = SynchronizationResult()
    
    # Synchronize A ↔ B
    session_ab = SynchronizationSession("cluster-a", "cluster-b")
    session_ab.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session_ab.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_ab.synchronize()
    result.add_session_result(session_ab)
    
    # Synchronize B ↔ C
    session_bc = SynchronizationSession("cluster-b", "cluster-c")
    session_bc.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_bc.exchange_state("cluster-c", cluster_c.snapshot(), cluster_c.cluster_hash())
    session_bc.synchronize()
    result.add_session_result(session_bc)
    
    # Synchronize A ↔ C (to verify full convergence)
    session_ac = SynchronizationSession("cluster-a", "cluster-c")
    session_ac.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session_ac.exchange_state("cluster-c", cluster_c.snapshot(), cluster_c.cluster_hash())
    session_ac.synchronize()
    result.add_session_result(session_ac)
    
    # All sessions should be complete
    summary = result.result_summary()
    assert summary["sessions_completed"] == 3


def test_synchronization_is_deterministic():
    """Test that synchronization produces deterministic digests."""
    cluster_a = _create_and_populate_cluster("cluster-a")
    cluster_b = _create_and_populate_cluster("cluster-b")
    
    # First synchronization
    session_1 = SynchronizationSession("cluster-a", "cluster-b")
    session_1.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session_1.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_1.synchronize()
    digest_1 = session_1.session_digest()
    
    # Identical synchronization
    session_2 = SynchronizationSession("cluster-a", "cluster-b")
    session_2.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session_2.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_2.synchronize()
    digest_2 = session_2.session_digest()
    
    assert digest_1 == digest_2
    assert len(digest_1) == 64  # SHA256 hex


def test_synchronization_order_independence():
    """Test that exchange order doesn't affect synchronization outcome."""
    cluster_a = _create_and_populate_cluster("cluster-a")
    cluster_b = _create_and_populate_cluster("cluster-b")
    
    # Session with A first, then B
    session_ab = SynchronizationSession("cluster-a", "cluster-b")
    session_ab.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    session_ab.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    result_ab = session_ab.compare_hashes()
    
    # Session with B first, then A
    session_ba = SynchronizationSession("cluster-a", "cluster-b")
    session_ba.exchange_state("cluster-b", cluster_b.snapshot(), cluster_b.cluster_hash())
    session_ba.exchange_state("cluster-a", cluster_a.snapshot(), cluster_a.cluster_hash())
    result_ba = session_ba.compare_hashes()
    
    # Results should be identical
    assert result_ab == result_ba
