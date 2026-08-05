from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SecurityMetrics:
    """
    Tracks security subsystem activity.
    """

    byzantine_events: int = 0

    attacks_detected: int = 0

    blocked_actions: int = 0

    allowed_actions: int = 0

    policy_checks: int = 0

    def record_byzantine_event(
        self,
    ) -> None:
        """
        Record Byzantine event.
        """

        self.byzantine_events += 1

    def record_attack(
        self,
    ) -> None:
        """
        Record detected attack.
        """

        self.attacks_detected += 1

    def record_blocked_action(
        self,
    ) -> None:
        """
        Record blocked operation.
        """

        self.blocked_actions += 1

    def record_allowed_action(
        self,
    ) -> None:
        """
        Record permitted operation.
        """

        self.allowed_actions += 1

    def record_policy_check(
        self,
    ) -> None:
        """
        Record policy evaluation.
        """

        self.policy_checks += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "byzantine_events":
                self.byzantine_events,

            "attacks_detected":
                self.attacks_detected,

            "blocked_actions":
                self.blocked_actions,

            "allowed_actions":
                self.allowed_actions,

            "policy_checks":
                self.policy_checks,
        }