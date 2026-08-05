from influx.state_sync.state_diff import (
    StateDiff,
)

from influx.state_sync.state_proof import (
    StateProof,
)


def test_create_proof():

    diff = StateDiff(
        added={
            "alice": 100,
        }
    )

    proof = StateProof.create(
        "root_old",
        "root_new",
        diff,
    )

    assert (
        proof.previous_root
        == "root_old"
    )

    assert (
        proof.new_root
        == "root_new"
    )

    assert isinstance(
        proof.diff_hash,
        str,
    )


def test_verify_valid_diff():

    diff = StateDiff(
        modified={
            "alice": 200,
        }
    )

    proof = StateProof.create(
        "old",
        "new",
        diff,
    )

    assert proof.verify_diff(
        diff
    )


def test_reject_modified_diff():

    original = StateDiff(
        added={
            "alice": 100,
        }
    )

    altered = StateDiff(
        added={
            "alice": 999,
        }
    )

    proof = StateProof.create(
        "old",
        "new",
        original,
    )

    assert (
        proof.verify_diff(
            altered
        )
        is False
    )


def test_snapshot():

    proof = StateProof(
        previous_root="a",
        new_root="b",
        diff_hash="c",
    )

    snapshot = proof.snapshot()

    assert (
        "previous_root"
        in snapshot
    )

    assert (
        "new_root"
        in snapshot
    )

    assert (
        "diff_hash"
        in snapshot
    )