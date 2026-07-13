from influx.contracts.manifest import ContractManifest
from influx.contracts.verifier import ContractVerifier


def create_manifest():
    return ContractManifest(
        contract_id="contract_a",
        owner="validator_001",
        version="1.0.0",
        code_hash="abc123",
    )


def test_valid_manifest_passes():

    verifier = ContractVerifier()

    assert verifier.verify(create_manifest())


def test_missing_contract_id_fails():

    verifier = ContractVerifier()

    manifest = ContractManifest(
        contract_id="",
        owner="validator_001",
        version="1.0.0",
        code_hash="abc123",
    )

    assert not verifier.verify(manifest)


def test_missing_code_hash_fails():

    verifier = ContractVerifier()

    manifest = ContractManifest(
        contract_id="contract_a",
        owner="validator_001",
        version="1.0.0",
        code_hash="",
    )

    assert not verifier.verify(manifest)


def test_identity_match():

    verifier = ContractVerifier()

    assert verifier.verify_identity(
        create_manifest(),
        create_manifest(),
    )


def test_identity_mismatch():

    verifier = ContractVerifier()

    other = ContractManifest(
        contract_id="contract_a",
        owner="validator_001",
        version="2.0.0",
        code_hash="abc123",
    )

    assert not verifier.verify_identity(
        create_manifest(),
        other,
    )


def test_verification_is_deterministic():

    verifier = ContractVerifier()

    first = verifier.verify(create_manifest())
    second = verifier.verify(create_manifest())

    assert first == second