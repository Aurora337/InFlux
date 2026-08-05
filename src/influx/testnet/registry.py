from __future__ import annotations

import hashlib
import json


SUPPORTED_ROLES = {"VN", "SN", "REN", "LN", "AN", "PTN"}


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: dict[str, dict] = {}

    def register(self, node: dict) -> dict:
        node_id = str(node.get("node_id", "")).strip()
        role = str(node.get("role", "")).strip()

        if not node_id:
            raise ValueError("node_id is required")
        if role not in SUPPORTED_ROLES:
            raise ValueError(f"unsupported role: {role}")
        if node_id in self._nodes:
            raise ValueError(f"duplicate node_id: {node_id}")

        canonical = {
            "node_id": node_id,
            "role": role,
        }
        self._nodes[node_id] = canonical
        return canonical

    def snapshot(self) -> list[dict]:
        return [self._nodes[key] for key in sorted(self._nodes)]

    def digest(self) -> str:
        payload = json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
