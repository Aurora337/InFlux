def verify_state_hash(
    state_hash: str,
    peer_hashes: list[str]
) -> bool:

    votes = 0

    for peer_hash in peer_hashes:

        if peer_hash == state_hash:
            votes += 1

    return votes > (len(peer_hashes) / 2)


__all__ = ["verify_state_hash"]
