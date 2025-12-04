"""ctor_sort.py

Placeholder ordering for CTOR pipeline.
"""

def ctor_sort(events: list) -> list:
    """Sort events deterministically (placeholder)."""
    return sorted(events, key=lambda e: str(e))

__all__ = ["ctor_sort"]
