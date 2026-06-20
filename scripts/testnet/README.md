# v0.7 Testnet Scripts

This directory contains initial scaffolding scripts for v0.7 testnet preparation.

## Scripts
- generate_genesis.py
- create_validator.py
- launch_validator.py
- bootstrap_network.py
- emit_snapshots.py
- emit_messages.py
- verify_network.py
- run_fault_scenarios.py
- exchange_state.py
- verify_state_sync.py
- run_catchup_sync.py
- run_staggered_catchup.py
- run_dual_offline_recovery.py
- run_partial_replay_stress.py
- run_partial_replay_matrix.py
- run_retry_exhaustion_suite.py
- run_backoff_latency_suite.py
- run_policy_comparison_suite.py
- run_sync_orchestration.py
- run_sync_orchestration_supervisor.py
- generate_sync_ops_runbook.py
- generate_sync_handoff_note.py
- validate_sync_ops_stability_gate.py

## Quick Start
Run from the repository root:

python launch_testnet.py

## v0.7.2 Outputs
- `testnet/launch/snapshots/*.json`
- `testnet/launch/network_health.json`

## v0.7.3 Outputs
- `testnet/messages/*.json`

## v0.7.4 Fault Modes
Run deterministic degraded scenarios from repository root:

- Snapshot hash divergence:
	- `python launch_testnet.py --fault-mode snapshot_hash_mismatch --fault-validator validator-3`
- Message hash mismatch:
	- `python launch_testnet.py --fault-mode message_hash_mismatch --fault-validator validator-3`
- Drop outbound handshake messages:
	- `python launch_testnet.py --fault-mode drop_outbound --fault-validator validator-3`

## v0.7.5 Fault Suite
- Run consolidated scenarios and produce report:
	- `python scripts/testnet/run_fault_scenarios.py`
- Output:
	- `testnet/launch/fault_report.json`
	- `testnet/launch/fault_report.md`

## v0.8.1 State Sync
- Build deterministic state payloads from snapshots:
	- `python scripts/testnet/exchange_state.py`
- Verify deterministic recovery and generate reports:
	- `python scripts/testnet/verify_state_sync.py`
- Outputs:
	- `testnet/launch/sync_report.json`
	- `testnet/launch/sync_report.md`

## v0.8.2 Catch-Up Sync
- Simulate offline validator recovery after missing blocks:
	- `python scripts/testnet/run_catchup_sync.py`

## v0.8.3 Staggered Catch-Up
- Run deterministic multi-validator catch-up scenarios one-by-one:
	- `python scripts/testnet/run_staggered_catchup.py`
- Consolidated outputs:
	- `testnet/launch/staggered_sync_report.json`
	- `testnet/launch/staggered_sync_report.md`

## v0.8.4 Dual Offline Recovery
- Run deterministic dual-offline recovery with quorum conflict-resolution checks:
	- `python scripts/testnet/run_dual_offline_recovery.py`
- Outputs:
	- `testnet/launch/dual_offline_report.json`
	- `testnet/launch/dual_offline_report.md`

## v0.8.5 Partial Replay Stress
- Run deterministic catch-up replay stress with chunked replay, timeout, and retry metrics:
	- `python scripts/testnet/run_partial_replay_stress.py`
- Outputs:
	- `testnet/launch/partial_replay_report.json`
	- `testnet/launch/partial_replay_report.md`

## v0.8.5 Partial Replay Matrix
- Run a deterministic matrix across multiple validators and replay profiles:
	- `python scripts/testnet/run_partial_replay_matrix.py`
- Consolidated outputs:
	- `testnet/launch/partial_replay_matrix_report.json`
	- `testnet/launch/partial_replay_matrix_report.md`

## v0.8.6 Retry Exhaustion Suite
- Validate deterministic recovery vs retry-exhaustion failure paths:
	- `python scripts/testnet/run_retry_exhaustion_suite.py`
- Suite outputs:
	- `testnet/launch/retry_exhaustion_suite.json`
	- `testnet/launch/retry_exhaustion_suite.md`

## v0.8.6 Backoff Latency Suite
- Validate deterministic backoff profiles against latency envelopes:
	- `python scripts/testnet/run_backoff_latency_suite.py`
- Suite outputs:
	- `testnet/launch/backoff_latency_suite.json`
	- `testnet/launch/backoff_latency_suite.md`

## v0.8.6 Policy Comparison Suite
- Compare deterministic retry policies and rank by score:
	- `python scripts/testnet/run_policy_comparison_suite.py`
- Suite outputs:
	- `testnet/launch/policy_comparison_suite.json`
	- `testnet/launch/policy_comparison_suite.md`

## v0.8.7 Sync Orchestration
- Run retry, latency, and policy suites as one orchestrated resilience pipeline:
	- `python scripts/testnet/run_sync_orchestration.py`
- Orchestration outputs:
	- `testnet/launch/sync_orchestration_report.json`
	- `testnet/launch/sync_orchestration_report.md`

## v0.8.7 Orchestration Supervisor
- Run orchestration with retry-and-escalation supervision:
	- `python scripts/testnet/run_sync_orchestration_supervisor.py`
- Supervisor outputs:
	- `testnet/launch/sync_orchestration_supervisor_report.json`
	- `testnet/launch/sync_orchestration_supervisor_report.md`

## v0.8.8 Sync Operations Runbook
- Generate operational incident guidance from suite and supervisor reports:
	- `python scripts/testnet/generate_sync_ops_runbook.py`
- Runbook outputs:
	- `testnet/launch/sync_ops_runbook.json`
	- `testnet/launch/sync_ops_runbook.md`

## v0.8.9 Timeline Appendix
- Runbook now includes deterministic incident timeline/event-log appendix derived from supervisor attempts and suite outcomes.

## v0.8.9 Handoff Note
- Generate a compact deterministic post-incident handoff note from runbook outputs:
	- `python scripts/testnet/generate_sync_handoff_note.py`
- Handoff outputs:
	- `testnet/launch/sync_ops_handoff_note.json`
	- `testnet/launch/sync_ops_handoff_note.md`

## v0.9.0 Stability Gate
- Validate deterministic consistency between runbook and handoff artifacts:
	- `python scripts/testnet/validate_sync_ops_stability_gate.py`
- Stability gate outputs:
	- `testnet/launch/sync_ops_stability_gate.json`
	- `testnet/launch/sync_ops_stability_gate.md`

## v0.9.0 Stability Scorecard
- Stability gate now emits deterministic release-readiness scorecard fields:
	- `readiness_score` (0-100)
	- `promotion_recommendation` (`promote`, `promote_with_monitoring`, `block`, `hold`)
	- `guidance` action list based on gate and operational state
