

from collections import Counter


def verify_state_hash(state_hash: str, peer_hashes: list[str]) -> bool:
    """
    Returns True only when state_hash has a strict majority
    among all peer hashes.
    """

    if not peer_hashes:
        return False

    counts = Counter(peer_hashes)
    votes = counts.get(state_hash, 0)

    return votes > (len(peer_hashes) / 2)