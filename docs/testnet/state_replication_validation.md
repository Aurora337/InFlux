# State Replication Validation (v1.3.3 Slice 2)

## Objective

Validate deterministic state replication across a validator set and deterministic
recovery replay behavior.

## Validation Contract

The state replication validator emits a deterministic JSON payload with:

- `replication_valid`
- `agreement_rate`
- `recovery_valid`
- `snapshot_exchange`
- `nodes_validated`
- `canonical_state_hash`
- `recovery_replay`
- `replay_steps`

## Deterministic Guarantees

- Canonical state hashing uses sorted-key JSON serialization.
- Every node receives the same replicated snapshot.
- Agreement rate is deterministic for fixed inputs.
- Recovery replay uses fixed replay steps and deterministic recovered state hash.

## Failure Behavior

- Invalid node count (`< 1`) raises `StateReplicationError`.

## Validation

Run:

```bash
python3 scripts/testnet/state_replication_validator.py
python -m pytest tests/testnet/test_state_replication.py -q
```
