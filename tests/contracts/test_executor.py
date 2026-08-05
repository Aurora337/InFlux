from influx.contracts import (
    Contract,
    ContractExecutor,
    ContractStorage,
    ExecutionContext,
)


def test_execute_contract() -> None:
    contract = Contract(
        contract_id="contract-1",
        owner="alice",
        version="1.0.0",
        code_hash="hash",
    )

    context = ExecutionContext(
        block_height=10,
        transaction_id="tx-123",
        caller="alice",
        network_id="ifx",
    )

    storage = ContractStorage()

    executor = ContractExecutor()

    result = executor.execute(
        contract,
        context,
        storage,
    )

    assert result.success is True
    assert result.contract_id == "contract-1"

    assert storage.get("last_transaction") == "tx-123"
    assert storage.get("last_caller") == "alice"
    assert storage.get("last_block") == "10"