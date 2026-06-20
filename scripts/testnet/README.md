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
