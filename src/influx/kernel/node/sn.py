"""State Node (SN) implementation with deterministic state hashing."""

from __future__ import annotations

import hashlib
import json


class StorageNode:
    def __init__(self, id: str):
        self.id = id
        self._state: dict[str, float] = {"height": 0.0, "reserve": 0.0, "circulation": 0.0}

    def apply_state_transition(self, delta: dict[str, float]) -> dict[str, float]:
        for key, value in sorted(delta.items()):
            self._state[key] = float(self._state.get(key, 0.0)) + float(value)
        return dict(self._state)

    def state_hash(self) -> str:
        canonical = json.dumps(self._state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def reproduce(self, *_args, **_kwargs):
        raise PermissionError("SN cannot perform reproduction operations")

    def verify_external_signature(self, *_args, **_kwargs):
        raise PermissionError("SN cannot verify external signatures")

    def status(self) -> dict:
        return {"id": self.id, "role": "SN"}


__all__ = ["StorageNode"]
