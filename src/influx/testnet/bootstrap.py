from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def load_genesis(genesis_path: Path) -> dict:
    payload = json.loads(genesis_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("genesis payload must be a JSON object")
    return payload


def _normalize_validators(validators: list[dict]) -> list[dict]:
    normalized = []
    for item in validators:
        node_id = str(item.get("node_id", "")).strip()
        role = str(item.get("role", "")).strip()
        if not node_id or not role:
            raise ValueError("validator entry requires non-empty node_id and role")
        normalized.append({"node_id": node_id, "role": role})
    return sorted(normalized, key=lambda entry: entry["node_id"])


def _bootstrap_payload(genesis: dict) -> dict:
    network_id = str(genesis.get("network_id", "ifx-testnet-001"))
    validators = _normalize_validators(list(genesis.get("validators", [])))
    reserve = float(genesis.get("reserve", 0.0))
    circulation = float(genesis.get("circulation", 0.0))
    clusters = list(genesis.get("clusters", [{"cluster_id": "cluster-1"}]))

    canonical_genesis = {
        "network_id": network_id,
        "validators": validators,
        "reserve": reserve,
        "circulation": circulation,
        "clusters": sorted(clusters, key=lambda item: str(item.get("cluster_id", ""))),
    }
    genesis_hash = hashlib.sha256(_canonical_json(canonical_genesis).encode("utf-8")).hexdigest()

    return {
        "network_id": network_id,
        "genesis_hash": genesis_hash,
        "validator_count": len(validators),
        "cluster_count": len(canonical_genesis["clusters"]),
        "node_registry": validators,
        "state": {
            "reserve": reserve,
            "circulation": circulation,
        },
    }


def bootstrap_from_genesis(genesis_path: Path) -> dict:
    genesis = load_genesis(genesis_path)
    return _bootstrap_payload(genesis)


def bootstrap_from_payload(genesis: dict) -> dict:
    return _bootstrap_payload(genesis)
