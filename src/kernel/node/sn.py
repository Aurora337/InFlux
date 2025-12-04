"""sn.py

Storage Node (SN) placeholder.
"""

class StorageNode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "SN"}

__all__ = ["StorageNode"]
