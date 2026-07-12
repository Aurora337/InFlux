from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .keystore import KeyStore, KeyEntry


class FileKeyStoreAdapter:
    """Simple JSON file adapter for KeyStore.

    The on-disk format is a mapping from account_id -> list of entries where each
    entry contains version, private_hex, public_hex, created_at, active.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, keystore: KeyStore) -> None:
        data: Dict[str, list] = {}
        for account_id in keystore._store.keys():
            data[account_id] = [
                {
                    "version": e.version,
                    "private_hex": e.private_hex,
                    "public_hex": e.public_hex,
                    "created_at": e.created_at,
                    "active": e.active,
                }
                for e in keystore.list_keys(account_id)
            ]

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)

    def load(self) -> KeyStore:
        ks = KeyStore()
        if not self.path.exists():
            return ks
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        for account_id, entries in raw.items():
            for item in entries:
                entry = KeyEntry(
                    version=item["version"],
                    private_hex=item["private_hex"],
                    public_hex=item["public_hex"],
                    created_at=item["created_at"],
                    active=item.get("active", True),
                )
                ks._store.setdefault(account_id, []).append(entry)
        return ks
