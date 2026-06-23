# Multi-Node Persistence (v1.3.4 Slice 1)

## Objective

Validate deterministic durable state storage and restart recovery for a fixed
validator set.

## Scope

- Persist validator state for each node to disk.
- Reload persisted state to simulate restart recovery.
- Verify canonical state hash consistency after reload.
- Emit deterministic milestone status payload.

## Deterministic Contract

The validator emits:

```json
{
  "persistence_valid": true,
  "nodes_persisted": 5,
  "durable_write_valid": true,
  "restart_recovery_valid": true,
  "state_hash_consistent": true
}
```

## Failure Conditions

Validation fails when:

- Any expected node state file is missing.
- Recovered state differs from originally persisted state.
- Canonical state hashes differ after restart recovery.
- Invalid node counts are supplied.

## Validation

Run:

```bash
python3 scripts/testnet/multi_node_persistence.py
python -m pytest tests/testnet/test_multi_node_persistence.py -q
```
