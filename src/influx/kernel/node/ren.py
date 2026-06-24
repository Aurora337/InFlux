"""Reproduction Node (REN) deterministic reserve response logic."""

from __future__ import annotations


class RelayNode:
    def __init__(self, id: str):
        self.id = id

    def responds_to_event(self, event_type: str) -> bool:
        return event_type == "VPU"

    def reproduction_signal(
        self,
        *,
        vpu: float,
        theta: float,
        t: float,
        alpha: float,
        beta: float,
        kappa: float,
        gamma: float,
    ) -> float:
        # R(t) = min(gamma, alpha*VPU + beta*Theta - kappa*t)
        return min(float(gamma), (float(alpha) * float(vpu)) + (float(beta) * float(theta)) - (float(kappa) * float(t)))

    def update_reserve(self, reserve: float, signal: float) -> float:
        return float(reserve) + float(signal)

    def update_circulation(self, *_args, **_kwargs):
        raise PermissionError("REN must never update circulation directly")

    def status(self) -> dict:
        return {"id": self.id, "role": "REN"}


__all__ = ["RelayNode"]
