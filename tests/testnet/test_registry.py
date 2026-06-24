import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.testnet.registry import NodeRegistry


def _join_sequence() -> list[dict]:
    return [
        {"node_id": "node-vn-1", "role": "VN"},
        {"node_id": "node-sn-1", "role": "SN"},
        {"node_id": "node-ren-1", "role": "REN"},
        {"node_id": "node-ln-1", "role": "LN"},
        {"node_id": "node-an-1", "role": "AN"},
        {"node_id": "node-ptn-1", "role": "PTN"},
    ]


def test_registry_registers_all_roles() -> None:
    registry = NodeRegistry()
    for node in _join_sequence():
        registry.register(node)

    snapshot = registry.snapshot()
    assert len(snapshot) == 6
    assert {item["role"] for item in snapshot} == {"VN", "SN", "REN", "LN", "AN", "PTN"}


def test_registry_hash_deterministic_for_identical_sequence() -> None:
    a = NodeRegistry()
    b = NodeRegistry()

    for node in _join_sequence():
        a.register(node)
    for node in _join_sequence():
        b.register(node)

    assert a.digest() == b.digest()


def test_registry_rejects_unsupported_role() -> None:
    registry = NodeRegistry()
    with pytest.raises(ValueError):
        registry.register({"node_id": "bad-1", "role": "UNKNOWN"})
