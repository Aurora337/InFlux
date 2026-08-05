import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.node.an import ArchiveNode
from influx.kernel.node.ln import LightNode
from influx.kernel.node.ptn import PTNNode
from influx.kernel.node.ren import RelayNode
from influx.kernel.node.sn import StorageNode
from influx.kernel.node.vn import ValidatorNode


def _build_certification_report() -> dict:
    vn = ValidatorNode("vn-1")
    sn = StorageNode("sn-1")
    ren = RelayNode("ren-1")
    ln = LightNode("ln-1")
    an = ArchiveNode("an-1")
    ptn = PTNNode("ptn-1")

    vn_verify_ok = vn.verify_event("abc", "abc") and vn.validate_hash("h1", "h1")
    vn_no_reproduce = False
    vn_no_reserve_mutation = False
    vn_no_circulation_transfer = False
    try:
        vn.reproduce()
    except PermissionError:
        vn_no_reproduce = True
    try:
        vn.mutate_reserve_supply()
    except PermissionError:
        vn_no_reserve_mutation = True
    try:
        vn.create_circulation_transfer()
    except PermissionError:
        vn_no_circulation_transfer = True
    vn_valid = vn_verify_ok and vn_no_reproduce and vn_no_reserve_mutation and vn_no_circulation_transfer

    pre_hash = sn.state_hash()
    sn.apply_state_transition({"height": 1, "reserve": 10.0})
    post_hash_a = sn.state_hash()
    post_hash_b = sn.state_hash()
    sn_state_transition_ok = pre_hash != post_hash_a
    sn_hash_deterministic = post_hash_a == post_hash_b
    sn_no_reproduce = False
    sn_no_external_sig_verify = False
    try:
        sn.reproduce()
    except PermissionError:
        sn_no_reproduce = True
    try:
        sn.verify_external_signature()
    except PermissionError:
        sn_no_external_sig_verify = True
    sn_valid = sn_state_transition_ok and sn_hash_deterministic and sn_no_reproduce and sn_no_external_sig_verify

    ren_vpu_only = ren.responds_to_event("VPU") and (not ren.responds_to_event("NON_VPU"))
    alpha = 0.6
    beta = 0.4
    kappa = 0.1
    gamma = 10.0
    vpu = 5.0
    theta = 2.0
    t = 3.0
    expected_signal = min(gamma, alpha * vpu + beta * theta - kappa * t)
    computed_signal = ren.reproduction_signal(
        vpu=vpu,
        theta=theta,
        t=t,
        alpha=alpha,
        beta=beta,
        kappa=kappa,
        gamma=gamma,
    )
    ren_formula_ok = computed_signal == expected_signal
    reserve_before = 100.0
    reserve_after = ren.update_reserve(reserve_before, computed_signal)
    ren_reserve_only_ok = reserve_after == reserve_before + expected_signal
    ren_no_circulation_update = False
    try:
        ren.update_circulation()
    except PermissionError:
        ren_no_circulation_update = True
    ren_valid = ren_vpu_only and ren_formula_ok and ren_reserve_only_ok and ren_no_circulation_update

    ln_summary = ln.query_summary({"height": 12, "state_hash": "hash-12", "reserve": 5})
    ln_read_only = False
    try:
        ln.mutate_state()
    except PermissionError:
        ln_read_only = True
    ln_valid = ln_summary == {"height": 12, "state_hash": "hash-12"} and ln_read_only

    an_snapshot_a = an.create_snapshot({"height": 12, "state_hash": "hash-12"})
    an_snapshot_b = an.create_snapshot({"height": 12, "state_hash": "hash-12"})
    an_valid = an_snapshot_a == an_snapshot_b

    ptn_route = ptn.route_platform_traffic({"event": "ping"}, "sn-1")
    ptn_no_mutation = False
    try:
        ptn.mutate_ledger()
    except PermissionError:
        ptn_no_mutation = True
    ptn_valid = ptn_route["routed"] is True and ptn_route["to"] == "sn-1" and ptn_no_mutation

    certified = all([vn_valid, sn_valid, ren_valid, ln_valid, an_valid, ptn_valid])
    return {
        "certified": certified,
        "vn_valid": vn_valid,
        "sn_valid": sn_valid,
        "ren_valid": ren_valid,
        "ln_valid": ln_valid,
        "an_valid": an_valid,
        "ptn_valid": ptn_valid,
    }


def test_node_role_isolation_certification_matches_artifact() -> None:
    expected_path = REPO_ROOT / "docs" / "audit" / "node_role_certification.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert _build_certification_report() == expected


def test_ren_formula_matches_specification() -> None:
    ren = RelayNode("ren-spec")
    alpha = 0.55
    beta = 0.25
    kappa = 0.05
    gamma = 9.0
    vpu = 4.0
    theta = 3.0
    t = 2.0

    expected = min(gamma, alpha * vpu + beta * theta - kappa * t)
    observed = ren.reproduction_signal(
        vpu=vpu,
        theta=theta,
        t=t,
        alpha=alpha,
        beta=beta,
        kappa=kappa,
        gamma=gamma,
    )
    assert observed == pytest.approx(expected)
