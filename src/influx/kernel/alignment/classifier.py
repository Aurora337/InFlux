"""classifier.py

Message classifier placeholder.
"""

def classify(msg: dict) -> str:
    return msg.get("type", "unknown")

__all__ = ["classify"]
