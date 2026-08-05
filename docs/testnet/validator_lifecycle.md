# Validator Lifecycle (v1.3.3 Slice 1)

## Objective

Implement a deterministic validator lifecycle state machine for testnet execution readiness.

## Lifecycle State Machine

CREATED -> REGISTERED -> STARTED -> HEALTHY -> STOPPED -> RECOVERED

`start_validator` transitions through STARTED and emits HEALTHY as the stable
runtime state for deterministic status output.

## Required Capabilities

- Create validator
- Register validator
- Start validator
- Stop validator
- Recover validator
- Emit deterministic lifecycle status

## Deterministic Contract

Running the lifecycle script must emit:

```json
{
  "validator_id": "validator-1",
  "state": "HEALTHY",
  "registered": true,
  "started": true,
  "healthy": true,
  "recoverable": true
}
```

## Transition Rules

- Invalid transitions are rejected with `LifecycleError`.
- Registration requires CREATED.
- Start requires REGISTERED.
- Stop requires HEALTHY.
- Recover requires STOPPED.

## Minimum Test Coverage

- `create_validator`
- `register_validator`
- `start_validator`
- `stop_validator`
- `recover_validator`
- `invalid_transition_rejected`
- `deterministic_output`

## Validation

Run:

```bash
python scripts/testnet/validator_lifecycle.py
python -m pytest tests/testnet/test_validator_lifecycle.py -q
```