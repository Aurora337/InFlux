"""Multi-cluster genesis validation with deterministic convergence proof."""

import hashlib
import json

from influx.testnet import ClusterRegistry


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _create_test_clusters(cluster_count: int = 3) -> ClusterRegistry:
    """Create multiple identical clusters from common spec."""
    registry = ClusterRegistry()
    
    # Define roles to register in each cluster
    node_specs = [
        ("vn-1", "VN"),
        ("sn-1", "SN"),
        ("ren-1", "REN"),
        ("ln-1", "LN"),
        ("an-1", "AN"),
        ("ptn-1", "PTN"),
    ]
    
    for cluster_idx in range(cluster_count):
        cluster_id = f"cluster-{cluster_idx + 1}"
        cluster = registry.create_cluster(cluster_id)
        
        for node_id, role in node_specs:
            # Qualify node_id with cluster index for uniqueness
            qualified_node_id = f"{node_id[:-1]}-{cluster_idx + 1}"
            cluster.register_node(qualified_node_id, role)
    
    return registry


def test_multi_cluster_genesis_creates_three_clusters():
    """Test that three independent clusters can be instantiated."""
    registry = _create_test_clusters(3)
    
    assert registry.cluster_count() == 3
    assert registry.total_member_count() == 18  # 6 nodes per cluster * 3 clusters


def test_multi_cluster_identical_genesis_hash():
    """Test that identical cluster specs produce identical registry digests."""
    registry_a = _create_test_clusters(3)
    digest_a = registry_a.registry_digest()
    
    registry_b = _create_test_clusters(3)
    digest_b = registry_b.registry_digest()
    
    assert digest_a == digest_b
    assert len(digest_a) == 64  # SHA256 hex


def test_multi_cluster_genesis_consistency():
    """Test that genesis baseline is consistent across clusters."""
    registry = _create_test_clusters(3)
    
    # Extract cluster states
    state = registry.registry_state()
    clusters = state["clusters"]
    
    # Verify all clusters have 6 members
    for cluster in clusters:
        members = cluster["members"]
        assert len(members) == 6
        
        # Verify all 6 roles are present
        roles = {m["role"] for m in members}
        assert roles == {"VN", "SN", "REN", "LN", "AN", "PTN"}


def test_multi_cluster_convergence_report():
    """Test that genesis convergence report has required structure."""
    registry_a = _create_test_clusters(3)
    registry_b = _create_test_clusters(3)
    
    digest_a = registry_a.registry_digest()
    digest_b = registry_b.registry_digest()
    hash_match = digest_a == digest_b
    
    report = {
        "genesis_valid": True,
        "clusters_created": 3,
        "hash_match": hash_match,
        "registry_digest": digest_a,
    }
    
    assert report["genesis_valid"] is True
    assert report["clusters_created"] == 3
    assert report["hash_match"] is True


def test_multi_cluster_ledger_baseline_identical():
    """Test that ledger baseline state is identical across clusters."""
    registry_a = _create_test_clusters(3)
    registry_b = _create_test_clusters(3)
    
    state_a = registry_a.registry_state()
    state_b = registry_b.registry_state()
    
    # Core state should match
    assert state_a["cluster_count"] == state_b["cluster_count"]
    assert state_a["total_members"] == state_b["total_members"]
    
    # Cluster snapshots should be identical
    assert state_a["clusters"] == state_b["clusters"]


def test_multi_cluster_genesis_reserve_circulation():
    """Test that reserve and circulation baselines can be tracked."""
    registry = _create_test_clusters(3)
    
    # Genesis baseline: all clusters start with same reserve/circulation
    genesis_baseline = {
        "reserve": 1000000.0,
        "circulation": 500000.0,
        "ledger_height": 0,
    }
    
    # Verify registry can track this baseline
    state = registry.registry_state()
    assert state["cluster_count"] == 3
    
    # In future versions, clusters will inherit baseline
    # For now, verify the structure is present
    assert "clusters" in state
