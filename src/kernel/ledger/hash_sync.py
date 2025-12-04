"""hash_sync.py

Hash synchronization utilities placeholder.
"""

import hashlib
from typing import List

def compute_root_hash(items: List[bytes]) -> str:
    h = hashlib.sha256()
    for item in items:
        h.update(item)
    return h.hexdigest()

__all__ = ["compute_root_hash"]
