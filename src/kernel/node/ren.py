"""ren.py

Relay Node (REN) placeholder.
"""

class RelayNode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "REN"}

__all__ = ["RelayNode"]
