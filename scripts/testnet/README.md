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
