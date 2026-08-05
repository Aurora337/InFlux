from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SecurityPolicy:
    """
    Defines security enforcement parameters.
    """

    max_faults: int = 3

    max_attack_severity: int = 10


class SecurityPolicyManager:
    """
    Manages deterministic security policies.
    """

    def __init__(
        self,
        policy: SecurityPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else SecurityPolicy()
        )

    def validator_allowed(
        self,
        faults: int,
    ) -> bool:
        """
        Determine validator eligibility.
        """

        return (
            faults
            < self.policy.max_faults
        )

    def attack_allowed(
        self,
        severity: int,
    ) -> bool:
        """
        Determine if attack severity is acceptable.
        """

        return (
            severity
            <= self.policy.max_attack_severity
        )