"""sgf.py

Sparse Gaussian Filter utilities (placeholder).
"""

from typing import List

def apply_sgf(data: List[float], kernel_size: int = 3) -> List[float]:
    """Apply a naive smoothing filter as a stand-in for SGF."""
    if kernel_size <= 1:
        return data[:]
    out = []
    n = len(data)
    half = kernel_size // 2
    for i in range(n):
        acc = 0.0
        count = 0
        for j in range(max(0, i - half), min(n, i + half + 1)):
            acc += data[j]
            count += 1
        out.append(acc / count if count else 0.0)
    return out

__all__ = ["apply_sgf"]
