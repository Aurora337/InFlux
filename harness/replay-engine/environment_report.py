"""Cross-environment determinism reporting utilities."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import platform
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "harness/replay-engine")
sys.path.insert(0, "harness/node-mesh-sim")

from influx.kernel.state import State
from replay_audit import audit_ledger_replay
from replay_scenario_runner import run_all_scenarios
from consensus_simulator import MultiNodeConsensusSimulator


@dataclass
class EnvironmentReport:
    environment: str
    generated_at: str
    platform_system: str
    platform_release: str
    platform_machine: str
    replay_blocks_checked: int
    replay_blocks_failed: int
    replay_determinism_score: float
    scenario_determinism_score: float
    consensus_agreement_rate: float
    final_state_hash: str
    ledger_integrity: str

    def to_dict(self) -> dict:
        return asdict(self)


def build_environment_report(
    environment: str,
    replay_data_dir: str = "data/blocks_demo_verify",
    scenarios_dir: str = "scenarios",
    scenario_output_root: str = "data/replays",
    consensus_rounds: int = 25,
) -> EnvironmentReport:
    initial_state = State(epoch=0, supply=1000.0, participants=100)

    replay = audit_ledger_replay(initial_state=initial_state, data_dir=replay_data_dir)
    scenario = run_all_scenarios(scenarios_dir=scenarios_dir, output_root=scenario_output_root)

    simulator = MultiNodeConsensusSimulator([
        "Validator-1",
        "Validator-2",
        "Validator-3",
        "Validator-4",
        "Validator-5",
    ])
    consensus = simulator.run(rounds=consensus_rounds, initial_state=initial_state)

    return EnvironmentReport(
        environment=environment,
        generated_at=datetime.now(timezone.utc).isoformat(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_machine=platform.machine(),
        replay_blocks_checked=replay.blocks_checked,
        replay_blocks_failed=replay.blocks_failed,
        replay_determinism_score=replay.determinism_score,
        scenario_determinism_score=float(scenario["determinism_score"]),
        consensus_agreement_rate=float(consensus["consensus_agreement_rate"]),
        final_state_hash=str(consensus["final_state_hash"]),
        ledger_integrity=str(replay.ledger_integrity),
    )


__all__ = ["EnvironmentReport", "build_environment_report"]
