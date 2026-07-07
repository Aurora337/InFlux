"""Golden test suite for cluster formation determinism and boundary enforcement."""

from influx.testnet import Cluster, ClusterMembership, ClusterRegistry


def test_cluster_creation_and_membership():
    """Test that a single cluster can register nodes with role validation."""
    cluster = Cluster("cluster-1")
    assert cluster.cluster_id == "cluster-1"
    assert cluster.member_count() == 0

    cluster.register_node("vn-1", "VN")
    cluster.register_node("sn-1", "SN")
    cluster.register_node("ren-1", "REN")
    cluster.register_node("ln-1", "LN")
    cluster.register_node("an-1", "AN")
    cluster.register_node("ptn-1", "PTN")

    assert cluster.member_count() == 6

    # Verify snapshot is deterministic
    snapshot_a = cluster.snapshot()
    snapshot_b = cluster.snapshot()
    assert snapshot_a == snapshot_b


def test_cluster_hash_deterministic():
    """Test that identical cluster membership sequences produce identical hashes."""
    cluster_a = Cluster("test-cluster")
    cluster_a.register_node("vn-1", "VN")
    cluster_a.register_node("sn-1", "SN")
    cluster_a.register_node("ren-1", "REN")
    hash_a = cluster_a.cluster_hash()

    cluster_b = Cluster("test-cluster")
    cluster_b.register_node("vn-1", "VN")
    cluster_b.register_node("sn-1", "SN")
    cluster_b.register_node("ren-1", "REN")
    hash_b = cluster_b.cluster_hash()

    assert hash_a == hash_b
    assert len(hash_a) == 64  # SHA256 hex is 64 characters


def test_cluster_membership_role_validation():
    """Test that unsupported roles are rejected."""
    cluster = Cluster("test-cluster")
    
    try:
        cluster.register_node("bad-1", "INVALID_ROLE")
        assert False, "Should have raised ValueError for invalid role"
    except ValueError as e:
        assert "not in" in str(e)


def test_cluster_membership_duplicate_rejection():
    """Test that duplicate node_ids are rejected."""
    cluster = Cluster("test-cluster")
    cluster.register_node("vn-1", "VN")
    
    try:
        cluster.register_node("vn-1", "SN")
        assert False, "Should have rejected duplicate node_id"
    except ValueError as e:
        assert "already registered" in str(e)


def test_cluster_registry_creation():
    """Test that registry can create and manage multiple clusters."""
    registry = ClusterRegistry()
    assert registry.cluster_count() == 0
    assert registry.total_member_count() == 0

    cluster_1 = registry.create_cluster("cluster-1")
    cluster_1.register_node("vn-1", "VN")
    cluster_1.register_node("sn-1", "SN")

    cluster_2 = registry.create_cluster("cluster-2")
    cluster_2.register_node("vn-2", "VN")
    cluster_2.register_node("sn-2", "SN")
    cluster_2.register_node("ren-2", "REN")

    assert registry.cluster_count() == 2
    assert registry.total_member_count() == 5


def test_cluster_registry_digest_deterministic():
    """Test that identical registry sequences produce identical digests."""
    registry_a = ClusterRegistry()
    c1_a = registry_a.create_cluster("cluster-1")
    c1_a.register_node("vn-1", "VN")
    c1_a.register_node("sn-1", "SN")
    c2_a = registry_a.create_cluster("cluster-2")
    c2_a.register_node("vn-2", "VN")
    c2_a.register_node("sn-2", "SN")
    digest_a = registry_a.registry_digest()

    registry_b = ClusterRegistry()
    c1_b = registry_b.create_cluster("cluster-1")
    c1_b.register_node("vn-1", "VN")
    c1_b.register_node("sn-1", "SN")
    c2_b = registry_b.create_cluster("cluster-2")
    c2_b.register_node("vn-2", "VN")
    c2_b.register_node("sn-2", "SN")
    digest_b = registry_b.registry_digest()

    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_cluster_registry_rejects_duplicate_cluster_id():
    """Test that duplicate cluster_ids are rejected."""
    registry = ClusterRegistry()
    registry.create_cluster("cluster-1")
    
    try:
        registry.create_cluster("cluster-1")
        assert False, "Should have rejected duplicate cluster_id"
    except ValueError as e:
        assert "already exists" in str(e)


def test_cluster_membership_snapshot_sorted():
    """Test that membership snapshots are sorted by node_id for determinism."""
    cluster = Cluster("test-cluster")
    cluster.register_node("zn-3", "VN")
    cluster.register_node("an-1", "SN")
    cluster.register_node("mn-2", "REN")
    
    snapshot = cluster.snapshot()
    members = snapshot["members"]
    node_ids = [m["node_id"] for m in members]
    
    assert node_ids == sorted(node_ids)
    assert node_ids == ["an-1", "mn-2", "zn-3"]


def test_cluster_state_immutability():
    """Test that cluster_state returns consistent immutable view."""
    cluster = Cluster("test-cluster")
    cluster.register_node("vn-1", "VN")
    
    state_a = cluster.cluster_state()
    state_b = cluster.cluster_state()
    
    assert state_a == state_b
    assert "cluster_hash" in state_a
    assert "membership_digest" in state_a
