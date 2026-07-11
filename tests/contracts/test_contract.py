from influx.contracts.contract import Contract


def test_contract_identity() -> None:
    contract = Contract(
        contract_id="contract-1",
        owner="alice",
        version="1.0.0",
        code_hash="deadbeef",
    )

    assert contract.identity() == "contract-1"
    assert contract.owner == "alice"
    assert contract.version == "1.0.0"