import random
from typing import Any, Dict, List


class ByzantineAdversary:
    """
    Simulates intentional malicious validator behavior.

    This is NOT random faulting — this is adversarial strategy simulation.
    """

    def __init__(self, seed: int = 1337):
        random.seed(seed)

    # -----------------------------
    # STATE MANIPULATION ATTACK
    # -----------------------------

    def forge_state(self, state: Any, aggression: float = 0.0) -> Any:
        """
        Attempts to subtly alter state proposals.
        """

        if random.random() < aggression:
            return {
                "forged": True,
                "original": state,
                "tamper_level": aggression
            }

        return state

    # -----------------------------
    # CONSENSUS DISRUPTION ATTACK
    # -----------------------------

    def split_vote(self, proposal: Dict[str, Any], aggression: float = 0.0) -> List[Dict[str, Any]]:
        """
        Simulates validator sending conflicting votes.
        """

        if random.random() < aggression:
            return [
                proposal,
                {
                    "state_hash": proposal["state_hash"],
                    "state": {"conflict": True},
                    "validator": proposal["validator"]
                }
            ]

        return [proposal]

    # -----------------------------
    # FAKE VALIDATOR WEIGHT MANIPULATION
    # -----------------------------

    def manipulate_weight(self, validator: Dict[str, Any], aggression: float = 0.0) -> Dict[str, Any]:
        """
        Attempts to distort perceived validator weight.
        """

        if random.random() < aggression:
            validator = validator.copy()
            validator["reputation"] = validator.get("reputation", 1.0) * 10

        return validator

    # -----------------------------
    # COORDINATED ATTACK SIMULATION
    # -----------------------------

    def coordinated_attack(
        self,
        proposals: List[Dict[str, Any]],
        aggression: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Simulates multiple validators acting maliciously together.
        """

        if random.random() < aggression:
            attacked = []

            for p in proposals:
                attacked.append({
                    **p,
                    "state": {
                        "corrupted": True,
                        "original_hash": p.get("state_hash")
                    }
                })

            return attacked

        return proposals