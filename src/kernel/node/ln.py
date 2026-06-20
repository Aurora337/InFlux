"""ln.py

Light Node (LN) placeholder.
"""

class LightNode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "LN"}

__all__ = ["LightNode"]
