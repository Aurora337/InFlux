"""Light Node (LN) read-only state access behavior."""

from __future__ import annotations


class LightNode:
    def __init__(self, id: str):
        self.id = id

    def query_summary(self, state: dict) -> dict:
        return {
            "height": state.get("height"),
            "state_hash": state.get("state_hash"),
        }

    def mutate_state(self, *_args, **_kwargs):
        raise PermissionError("LN is read-only and cannot mutate state")

    def status(self) -> dict:
        return {"id": self.id, "role": "LN"}


__all__ = ["LightNode"]
