from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from influx.kernel.node.vn import ValidatorNode
from influx.kernel.sync.shcm import verify_state_hash


def _simulate_network(consensus_override: list[str] | None = None):
    state = State(epoch=0, supply=1000.0, participants=100)
    next_state = process_pipeline(state)

    validators = [ValidatorNode("Node A"), ValidatorNode("Node B"), ValidatorNode("Node C")]
    node_hashes = []

    for validator in validators:
        local_hash = compute_root_hash(serialize_state(next_state))
        node_hashes.append((validator, local_hash))

    peer_hashes = [local_hash for _, local_hash in node_hashes]
    if consensus_override is not None:
        peer_hashes = consensus_override

    network_hash = peer_hashes[0]
    validations = [
        validator.validate_hash(local_hash, network_hash)
        for validator, local_hash in node_hashes
    ]

    consensus_ok = verify_state_hash(network_hash, peer_hashes)
    approved_state = next_state if consensus_ok else None

    return {
        "state": state,
        "next_state": next_state,
        "node_hashes": node_hashes,
        "validations": validations,
        "consensus_ok": consensus_ok,
        "approved_state": approved_state,
    }


def test_network_simulation_approved_state_on_consensus_true():
    result = _simulate_network()

    assert result["consensus_ok"]
    assert result["approved_state"] == result["next_state"]


def test_network_simulation_rejects_state_on_consensus_false():
    result = _simulate_network(
        consensus_override=[
            "aaa111",
            "bbb222",
            "ccc333",
        ]
    )

    assert not result["consensus_ok"]
    assert result["approved_state"] is None
