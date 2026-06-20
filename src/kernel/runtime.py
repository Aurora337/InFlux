from state import State

try:
    from kernel.ledger.pipeline import process_pipeline
    from kernel.ledger.serialization import serialize_state
    from kernel.ledger.hash_sync import compute_root_hash
    from kernel.node.vn import ValidatorNode
    from kernel.sync.shcm import verify_state_hash
except ModuleNotFoundError:
    from ledger.pipeline import process_pipeline
    from ledger.serialization import serialize_state
    from ledger.hash_sync import compute_root_hash
    from node.vn import ValidatorNode
    from sync.shcm import verify_state_hash


def main():

    state = State(
        epoch=0,
        supply=1000.0,
        participants=100
    )

    print("\nINITIAL STATE")
    print(state)

    state = process_pipeline(state)

    print("\nNEXT STATE")
    print(state)

    serialized = serialize_state(state)

    state_hash = compute_root_hash(serialized)

    print("\nSTATE HASH")
    print(state_hash)

    validators = [ValidatorNode("Node A"), ValidatorNode("Node B"), ValidatorNode("Node C")]

    node_hashes = []
    for validator in validators:
        local_serialized = serialize_state(state)
        local_hash = compute_root_hash(local_serialized)
        node_hashes.append((validator, local_hash))

    peer_hashes = [local_hash for _, local_hash in node_hashes]
    network_hash = peer_hashes[0]
    validations = [
        validator.validate_hash(local_hash, network_hash)
        for validator, local_hash in node_hashes
    ]
    consensus_ok = verify_state_hash(network_hash, peer_hashes)

    print("\nNODE HASHES")
    for validator, local_hash in node_hashes:
        print({"node": validator.node_id, "hash": local_hash})

    print("\nCONSENSUS")
    print(consensus_ok)

    print("\nAPPROVED STATE")
    print(state if consensus_ok else "REJECTED")


if __name__ == "__main__":
    main()