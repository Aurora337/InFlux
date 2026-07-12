from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .accounts import WalletAccount
from .keystore import KeyStore
from .keystore_adapter import FileKeyStoreAdapter


class WalletManager:
    """Simple wallet account manager with JSON persistence and KeyStore integration."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.accounts_dir = storage_dir / "accounts"
        self.ks_path = storage_dir / "keystore.json"
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        self.ks_adapter = FileKeyStoreAdapter(self.ks_path)
        self.keystore = self.ks_adapter.load()

    def create_account(self, account_id: str, identity_id: str, created_at: int) -> WalletAccount:
        account = WalletAccount(account_id=account_id, identity_id=identity_id, created_at=created_at)
        # persist
        path = self.accounts_dir / f"{account_id}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(account.to_dict(), fh, indent=2, sort_keys=True)
        return account

    def load_account(self, account_id: str) -> Optional[WalletAccount]:
        path = self.accounts_dir / f"{account_id}.json"
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        account = WalletAccount(
            account_id=raw["account_id"],
            identity_id=raw["identity_id"],
            created_at=raw["created_at"],
            active=raw.get("active", True),
            addresses=raw.get("addresses", []),
        )
        # sync key_version from keystore
        account.set_active_key_from_keystore(self.keystore)
        return account

    def add_key_for_account(self, account_id: str, private_hex: str, public_hex: str, created_at: int):
        entry = self.keystore.add_key(account_id, private_hex, public_hex, created_at)
        self.ks_adapter.save(self.keystore)
        # update account JSON if exists
        path = self.accounts_dir / f"{account_id}.json"
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            raw["key_version"] = entry.version
            path.write_text(json.dumps(raw, indent=2, sort_keys=True), encoding="utf-8")
        return entry
