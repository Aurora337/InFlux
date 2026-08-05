from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class KeyEntry:
    version: int
    private_hex: str
    public_hex: str
    created_at: int
    active: bool = True


class KeyStore:
    """In-memory keystore for account key versions.

    This is a simple implementation intended for tests and local tooling.
    Production should use secure storage (KMS/HSM) and encrypted blobs.
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[KeyEntry]] = {}

    def add_key(self, account_id: str, private_hex: str, public_hex: str, created_at: int) -> KeyEntry:
        entries = self._store.setdefault(account_id, [])
        version = (entries[-1].version + 1) if entries else 1
        entry = KeyEntry(version=version, private_hex=private_hex, public_hex=public_hex, created_at=created_at)
        # mark previous entries inactive
        for e in entries:
            e.active = False
        entries.append(entry)
        return entry

    def get_active_key(self, account_id: str) -> Optional[KeyEntry]:
        entries = self._store.get(account_id, [])
        for e in reversed(entries):
            if e.active:
                return e
        return None

    def get_key_by_version(self, account_id: str, version: int) -> Optional[KeyEntry]:
        entries = self._store.get(account_id, [])
        for e in entries:
            if e.version == version:
                return e
        return None

    def rotate_key(self, account_id: str, private_hex: str, public_hex: str, created_at: int) -> KeyEntry:
        return self.add_key(account_id, private_hex, public_hex, created_at)

    def list_keys(self, account_id: str) -> List[KeyEntry]:
        return list(self._store.get(account_id, []))
