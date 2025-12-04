"""vn.py

Validator Node (VN) placeholder.
"""

class ValidatorNode:
    def __init__(self, id: str):
        self.id = id

    def status(self) -> dict:
        return {"id": self.id, "role": "VN"}

__all__ = ["ValidatorNode"]
