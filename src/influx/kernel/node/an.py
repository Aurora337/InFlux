"""Archive Node (AN) deterministic snapshot behavior."""

from __future__ import annotations

import hashlib
import json


class ArchiveNode:
    def __init__(self, id: str):
        self.id = id

    def create_snapshot(self, state: dict) -> dict:
        canonical = json.dumps(state, sort_keys=True, separators=(",", ":"))
        return {
            "hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "state": dict(state),
        }

    def status(self) -> dict:
        return {"id": self.id, "role": "AN"}


__all__ = ["ArchiveNode"]
