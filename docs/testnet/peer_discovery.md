# Peer Discovery Validation (v1.3.3 Slice 3)

## Purpose

Validate deterministic peer discovery across the validator network before testnet
promotion.

## Input Artifacts

The validator can ingest these artifacts when present:

- `testnet/peers/peers.json`
- `testnet/validators/*.json`
- `testnet/launch/network_health.json`

If artifacts are not present, deterministic fallback fixtures are used to keep
validation reproducible.

## Validation Rules

The validator checks:

- Peer Registration
- Peer Enumeration
- Peer Lookup
- Membership Consistency
- Expected Peer Count
- Network Health Consistency

## Output Schema

The script emits a deterministic JSON payload:

```json
{
  "peer_discovery_valid": true,
  "peers_found": 5,
  "membership_consistent": true,
  "duplicate_peers": 0,
  "missing_peers": 0
}
```

## Failure Conditions

Validation fails when any of the following are detected:

- Duplicate peer IDs in registry
- Missing peers compared with validator membership
- Mismatch between discovered peers and expected peer count
- Network health inconsistency

## Validation

Run:

```bash
python3 scripts/testnet/peer_discovery.py
python -m pytest tests/testnet/test_peer_discovery.py -q
```
