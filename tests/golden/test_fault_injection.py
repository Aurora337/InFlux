import sys

sys.path.insert(0, "harness/node-mesh-sim")

from fault_injection_harness import run_fault_injection_scenario, run_fault_suite


def test_fault_injection_validator_dropout_passes():
    payload = run_fault_injection_scenario("scenarios/fault/validator_dropout.json")

    assert payload["scenario"] == "validator_dropout"
    assert payload["rounds_checked"] == 25
    assert payload["rounds_failed"] == 0
    assert payload["fault_rounds"] == 1
    assert payload["fault_recovered"] == 1
    assert payload["recovery_rate"] == 1.0
    assert payload["agreement_rate"] == 1.0
    assert payload["divergence_count"]["Validator-C"] >= 1


def test_fault_injection_suite_runs():
    payload = run_fault_suite("scenarios/fault")

    assert payload["scenarios_checked"] == 6
    assert payload["scenarios_passed"] == 6
    assert payload["scenarios_failed"] == 0
    assert payload["agreement_rate"] > 0.0
    assert payload["recovery_rate"] > 0.0
    assert payload["replay_success_rate"] > 0.0
