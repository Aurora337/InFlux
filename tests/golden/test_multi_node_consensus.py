import sys

sys.path.insert(0, "src")
sys.path.insert(0, "harness/node-mesh-sim")

from influx.kernel.state import State
from consensus_simulator import MultiNodeConsensusSimulator


def _validators() -> list[str]:
    return ["Validator-1", "Validator-2", "Validator-3", "Validator-4", "Validator-5"]


def test_multi_node_consensus_perfect_agreement():
    simulator = MultiNodeConsensusSimulator(_validators())
    result = simulator.run(
        rounds=20,
        initial_state=State(epoch=0, supply=1000.0, participants=100),
    )

    assert result["rounds_checked"] == 20
    assert result["rounds_passed"] == 20
    assert result["rounds_failed"] == 0
    assert result["consensus_agreement_rate"] == 1.0
    assert all(count == 0 for count in result["divergence_counts"].values())


def test_multi_node_consensus_with_fault_injection():
    simulator = MultiNodeConsensusSimulator(_validators())
    result = simulator.run(
        rounds=10,
        initial_state=State(epoch=0, supply=1000.0, participants=100),
        fault_schedule={3: ["Validator-5"], 4: ["Validator-5"], 7: ["Validator-2"]},
    )

    assert result["rounds_checked"] == 10
    assert result["rounds_passed"] == 10
    assert result["rounds_failed"] == 0
    assert result["consensus_agreement_rate"] < 1.0
    assert result["divergence_counts"]["Validator-5"] == 2
    assert result["divergence_counts"]["Validator-2"] == 1
