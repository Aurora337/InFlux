"""an.py

Archive Node (AN) placeholder.
"""

class ArchiveNode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "AN"}

__all__ = ["ArchiveNode"]
