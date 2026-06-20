#!/usr/bin/env python3
"""Run 5-validator consensus simulation and emit agreement metrics."""

import argparse
import json
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "harness/node-mesh-sim")

from kernel.state import State
from consensus_simulator import MultiNodeConsensusSimulator


def _default_validator_ids(count: int) -> list[str]:
    return [f"Validator-{index}" for index in range(1, count + 1)]


def main() -> int:
    parser = argparse.ArgumentParser(description="InFlux multi-node consensus simulation")
    parser.add_argument("--validators", type=int, default=5, help="Number of validator nodes")
    parser.add_argument("--rounds", type=int, default=25, help="Number of consensus rounds")
    parser.add_argument("--epoch", type=int, default=0, help="Initial epoch")
    parser.add_argument("--supply", type=float, default=1000.0, help="Initial supply")
    parser.add_argument("--participants", type=int, default=100, help="Initial participants")
    parser.add_argument("--verbose", action="store_true", help="Include per-round details")
    args = parser.parse_args()

    simulator = MultiNodeConsensusSimulator(_default_validator_ids(args.validators))
    initial_state = State(
        epoch=args.epoch,
        supply=args.supply,
        participants=args.participants,
    )
    payload = simulator.run(rounds=args.rounds, initial_state=initial_state)

    if not args.verbose:
        payload = {
            "validators": payload["validators"],
            "rounds_checked": payload["rounds_checked"],
            "rounds_passed": payload["rounds_passed"],
            "rounds_failed": payload["rounds_failed"],
            "consensus_agreement_rate": payload["consensus_agreement_rate"],
            "divergence_counts": payload["divergence_counts"],
            "final_epoch": payload["final_epoch"],
            "final_state_hash": payload["final_state_hash"],
        }

    print(json.dumps(payload, indent=2))

    if payload["rounds_failed"] == 0 and payload["consensus_agreement_rate"] == 1.0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
