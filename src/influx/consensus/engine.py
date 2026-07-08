from typing import Any, Dict, List

from influx.crypto.hash import DeterministicHasher


class ConsensusEngine:
    """
    Deterministic Finality Consensus Engine.

    This version enforces:
    - multi-proposal evaluation
    - weighted deterministic selection
    - fork resolution
    - finality locking
    """

    def __init__(self, config: dict):
        self.config = config
        self.initialized = False
        self.final_state_hash: str | None = None

    def initialize(self) -> None:
        self.initialized = True

    # -----------------------------
    # VALIDATOR WEIGHT MODEL
    # -----------------------------

    def compute_validator_weight(self, validator: Dict[str, Any]) -> float:
        return (
            validator.get("reputation", 1.0)
            * validator.get("uptime", 1.0)
            * validator.get("accuracy", 1.0)
        )

    # -----------------------------
    # PROPOSAL GENERATION
    # -----------------------------

    def propose_state(self, state: Any, validator: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "state": state,
            "state_hash": DeterministicHasher.hash(state),
            "validator": validator
        }

    # -----------------------------
    # MULTI-PROPOSAL CONSENSUS
    # -----------------------------

    def evaluate_votes(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Deterministic weighted consensus selection.
        """

        if not proposals:
            return {"status": "rejected", "reason": "no_proposals"}

        score_map: Dict[str, float] = {}
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        # Group proposals by state hash
        for p in proposals:
            h = p["state_hash"]
            grouped.setdefault(h, []).append(p)

        # Compute weighted scores
        for h, group in grouped.items():
            score = 0.0

            for p in group:
                weight = self.compute_validator_weight(p["validator"])
                score += weight

            score_map[h] = score

        # Deterministic selection (tie-break via hash ordering)
        selected = sorted(
            score_map.items(),
            key=lambda x: (-x[1], x[0])
        )[0][0]

        return {
            "selected_state_hash": selected,
            "scores": score_map,
            "groups": grouped
        }

    # -----------------------------
    # FINALITY RULES
    # -----------------------------

    def finalize_state(self, consensus_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Locks final system state.
        """

        final_hash = DeterministicHasher.hash(
            self._canonicalize(consensus_result)
        )

        self.final_state_hash = final_hash

        return {
            "final_state_hash": final_hash,
            "consensus_result": consensus_result,
            "finalized": True
        }
    
    def _canonicalize(self, obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: self._canonicalize(obj[k]) for k in sorted(obj)}
        
            if isinstance(obj, list):
                return sorted(
                    [self._canonicalize(x) for x in obj],
                    key=lambda x: DeterministicHasher.hash(x)
                )

            return obj

    # -----------------------------
    # FORK RESOLUTION
    # -----------------------------

    def resolve_fork(self, competing_states: List[Any]) -> Any:
        """
        Deterministic fork resolution via hash ordering.
        """

        hashed = [
            (DeterministicHasher.hash(s), s)
            for s in competing_states
        ]

        # Highest hash wins deterministically (stable ordering rule)
        return sorted(hashed, key=lambda x: x[0])[-1][1]