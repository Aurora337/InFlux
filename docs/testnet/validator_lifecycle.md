# Validator Lifecycle (v1.3.3 Slice 1)

## Objective

Implement a deterministic validator lifecycle state machine for testnet execution readiness.

## Lifecycle Stages

1. Creation
2. Registration
3. Startup
4. Shutdown
5. Recovery

## Deterministic Contract

Running the lifecycle script must emit:

```json
{
  "validator_id": "validator-1",
  "registered": true,
  "started": true,
  "healthy": true,
  "recoverable": true
}
```

## Implementation Notes

- Transitions are order-enforced and raise errors when out of sequence.
- Recovery requires prior shutdown.
- The final state after recovery is started and healthy.

## Validation

Run:

```bash
python scripts/testnet/validator_lifecycle.py
python -m pytest tests/testnet/test_validator_lifecycle.py -q
```