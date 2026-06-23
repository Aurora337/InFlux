"""Multi-node consensus simulation for deterministic hash agreement metrics."""

from collections import Counter
from dataclasses import dataclass
import sys

sys.path.insert(0, "src")

from influx.kernel.state import State
from influx.kernel.node.vn import ValidatorNode
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from influx.kernel.sync.shcm import verify_state_hash


@dataclass
class RoundResult:
    round_index: int
    network_hash: str
    peer_hashes: list[str]
    agreement_rate: float
    consensus_passed: bool
    approved_state_epoch: int


class MultiNodeConsensusSimulator:
    def __init__(self, validator_ids: list[str]):
        self.validators = [ValidatorNode(node_id) for node_id in validator_ids]

    @staticmethod
    def _hash_state(state: State) -> str:
        return compute_root_hash(serialize_state(state))

    @staticmethod
    def _select_network_hash(peer_hashes: list[str]) -> str:
        counts = Counter(peer_hashes)
        return counts.most_common(1)[0][0]

    def run(
        self,
        rounds: int,
        initial_state: State,
        fault_schedule: dict[int, list[str]] | None = None,
    ) -> dict:
        fault_schedule = fault_schedule or {}
        current_state = initial_state
        round_results: list[RoundResult] = []
        divergence_counts = {validator.node_id: 0 for validator in self.validators}

        for round_index in range(1, rounds + 1):
            next_state = process_pipeline(current_state)
            canonical_hash = self._hash_state(next_state)

            peer_hashes: list[str] = []
            for validator in self.validators:
                local_hash = canonical_hash
                if validator.node_id in fault_schedule.get(round_index, []):
                    local_hash = f"tampered-{validator.node_id}-{round_index}"
                peer_hashes.append(local_hash)

            network_hash = self._select_network_hash(peer_hashes)
            validations = [
                validator.validate_hash(local_hash, network_hash)
                for validator, local_hash in zip(self.validators, peer_hashes)
            ]

            for validator, accepted in zip(self.validators, validations):
                if not accepted:
                    divergence_counts[validator.node_id] += 1

            agreement_rate = sum(1 for accepted in validations if accepted) / len(validations)
            consensus_passed = verify_state_hash(network_hash, peer_hashes)

            if consensus_passed:
                current_state = next_state

            round_results.append(
                RoundResult(
                    round_index=round_index,
                    network_hash=network_hash,
                    peer_hashes=peer_hashes,
                    agreement_rate=agreement_rate,
                    consensus_passed=consensus_passed,
                    approved_state_epoch=current_state.epoch,
                )
            )

        consensus_agreement_rate = (
            sum(result.agreement_rate for result in round_results) / len(round_results)
            if round_results
            else 0.0
        )
        rounds_passed = sum(1 for result in round_results if result.consensus_passed)

        return {
            "validators": [validator.node_id for validator in self.validators],
            "rounds_checked": rounds,
            "rounds_passed": rounds_passed,
            "rounds_failed": rounds - rounds_passed,
            "consensus_agreement_rate": consensus_agreement_rate,
            "divergence_counts": divergence_counts,
            "final_epoch": current_state.epoch,
            "final_state_hash": self._hash_state(current_state),
            "details": [
                {
                    "round": result.round_index,
                    "network_hash": result.network_hash,
                    "peer_hashes": result.peer_hashes,
                    "agreement_rate": result.agreement_rate,
                    "consensus_passed": result.consensus_passed,
                    "approved_state_epoch": result.approved_state_epoch,
                }
                for result in round_results
            ],
        }


__all__ = ["MultiNodeConsensusSimulator", "RoundResult"]
