"""ptn.py

Peer-to-peer transit node (PTN) placeholder.
"""

class PTNNode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "PTN"}

__all__ = ["PTNNode"]
