"""fi_node.py

Financial Institution node (FI) placeholder.
"""

class FINode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "FI"}

__all__ = ["FINode"]
