# Network Recovery Validation (v1.3.4 Slice 3)

## Purpose

Validate deterministic recovery of validator membership and consensus after
single-node, multi-node, and full-network restart disruptions.

## Recovery Scenarios

1. Single validator failure and rejoin.
2. Multiple validator failure and recovery.
3. Full validator restart and registry rebuild.

## Fault Injection Integration

The validator accepts these deterministic fault modes aligned with v0.7.x:

- `snapshot_hash_mismatch`
- `message_hash_mismatch`
- `drop_outbound`

Validation verifies that recoverable faults return the network to healthy
membership and consensus state.

## Output Schema

```json
{
  "network_recovery_valid": true,
  "validators_expected": 5,
  "validators_recovered": 5,
  "membership_restored": true,
  "consensus_restored": true,
  "canonical_hash_consistent": true,
  "recovery_score": 1.0
}
```

## Validation

Run:

```bash
python3 scripts/testnet/network_recovery_validator.py
python -m pytest tests/testnet/test_network_recovery.py -q
```
