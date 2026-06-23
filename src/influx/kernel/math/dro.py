"""dro.py

Deterministic Range Operations (placeholder).
"""

def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value to deterministic bounds."""
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value

__all__ = ["clamp"]
