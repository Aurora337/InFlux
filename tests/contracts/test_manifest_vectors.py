from influx.contracts.manifest import ContractManifest


def create_manifest():
    return ContractManifest(
        contract_id="contract_a",
        owner="validator_001",
        version="1.0.0",
        code_hash="abc123",
    )


def test_manifest_creation():
    manifest = create_manifest()

    assert manifest.contract_id == "contract_a"


def test_manifest_export():
    manifest = create_manifest()

    data = manifest.to_dict()

    assert data["owner"] == "validator_001"
    assert data["version"] == "1.0.0"


def test_manifest_identity_is_deterministic():
    first = create_manifest()
    second = create_manifest()

    assert first.identity() == second.identity()


def test_different_code_hash_changes_identity():
    first = create_manifest()

    second = ContractManifest(
        contract_id="contract_a",
        owner="validator_001",
        version="1.0.0",
        code_hash="different",
    )

    assert first.identity() != second.identity()


def test_manifest_is_immutable():
    manifest = create_manifest()

    try:
        manifest.version = "2.0.0"
    except Exception:
        assert True
    else:
        assert False


def test_manifest_dictionary_is_complete():
    manifest = create_manifest()

    data = manifest.to_dict()

    assert set(data.keys()) == {
        "contract_id",
        "owner",
        "version",
        "code_hash",
    }