from influx.contracts.serializer import ContractSerializer


def create_metadata():
    return {
        "owner": "validator_001",
        "version": "1.0.0",
        "code_hash": "abcdef123456",
    }


def test_round_trip_serialization():
    metadata = create_metadata()

    serialized = ContractSerializer.serialize(metadata)
    restored = ContractSerializer.deserialize(serialized)

    assert restored == metadata


def test_serialization_is_deterministic():
    metadata = create_metadata()

    first = ContractSerializer.serialize(metadata)
    second = ContractSerializer.serialize(metadata)

    assert first == second


def test_key_order_does_not_change_output():
    first = {
        "owner": "validator_001",
        "version": "1.0.0",
        "code_hash": "abcdef123456",
    }

    second = {
        "code_hash": "abcdef123456",
        "version": "1.0.0",
        "owner": "validator_001",
    }

    assert (
        ContractSerializer.serialize(first)
        == ContractSerializer.serialize(second)
    )


def test_deserialize_returns_expected_values():
    payload = (
        '{"code_hash":"abcdef123456",'
        '"owner":"validator_001",'
        '"version":"1.0.0"}'
    )

    metadata = ContractSerializer.deserialize(payload)

    assert metadata["owner"] == "validator_001"
    assert metadata["version"] == "1.0.0"
    assert metadata["code_hash"] == "abcdef123456"


def test_empty_dictionary_round_trip():
    serialized = ContractSerializer.serialize({})
    restored = ContractSerializer.deserialize(serialized)

    assert restored == {}


def test_serialized_output_is_stable():
    metadata = create_metadata()

    expected = (
        '{"code_hash":"abcdef123456",'
        '"owner":"validator_001",'
        '"version":"1.0.0"}'
    )

    assert ContractSerializer.serialize(metadata) == expected