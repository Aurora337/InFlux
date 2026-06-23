# Node Restart Recovery Validation (v1.3.4 Slice 2)

## Recovery Sequence

1. Node starts.
2. Node state is persisted as a snapshot.
3. Node stops.
4. Node restarts.
5. Persisted snapshot is loaded and validated.

## Persistence Requirements

- Each validator must produce one deterministic snapshot file.
- Snapshot payload must be valid JSON.
- Snapshot must contain the canonical state fields needed for hash verification.

## Failure Modes

The validator simulates deterministic recovery behavior for:

- Unexpected shutdown
- Missing snapshot
- Corrupted snapshot
- Delayed restart

## Validation Metrics

- `recovery_valid`
- `restart_success_rate`
- `state_restored`
- `hash_consistent`
- `peer_membership_restored`
- `missing_snapshot_detected`
- `corrupted_snapshot_detected`

## Output Schema

```json
{
  "recovery_valid": true,
  "restart_success_rate": 1.0,
  "state_restored": true,
  "hash_consistent": true,
  "peer_membership_restored": true,
  "missing_snapshot_detected": false,
  "corrupted_snapshot_detected": false,
  "restart_delay_applied_ms": 0
}
```

## Validation

Run:

```bash
python3 scripts/testnet/node_recovery_validator.py
python -m pytest tests/testnet/test_node_recovery.py -q
```
