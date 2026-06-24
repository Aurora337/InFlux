"""Platform Transit Node (PTN) deterministic routing behavior."""

from __future__ import annotations


class PTNNode:
    def __init__(self, id: str):
        self.id = id

    def route_platform_traffic(self, message: dict, target: str) -> dict:
        return {
            "from": self.id,
            "to": target,
            "message": dict(message),
            "routed": True,
        }

    def mutate_ledger(self, *_args, **_kwargs):
        raise PermissionError("PTN cannot mutate ledger state")

    def status(self) -> dict:
        return {"id": self.id, "role": "PTN"}


__all__ = ["PTNNode"]
