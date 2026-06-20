import hashlib


def compute_root_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
