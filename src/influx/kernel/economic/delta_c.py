"""
In-Flux Deterministic Economic Engine
"""

BASE_GROWTH_RATE = 0.01


def compute_delta(supply: float, participants: int) -> float:

    participation_factor = max(participants, 1)

    delta = (
        supply
        * BASE_GROWTH_RATE
        * (participation_factor / 100)
    )

    return round(delta, 8)
