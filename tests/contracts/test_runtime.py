from influx.contracts import (
    Contract,
    ContractABI,
    ContractRuntime,
    ContractStorage,
    EventEmitter,
    ExecutionContext,
    GasMeter,
)


def test_runtime_registration() -> None:
    runtime = ContractRuntime()

    contract = Contract(
        contract_id="contract-1",
        owner="alice",
        version="1.0.0",
        code_hash="abc123",
    )

    runtime.register(contract)

    assert runtime.registered() == 1
    assert runtime.get("contract-1") == contract


def test_runtime_execute() -> None:
    runtime = ContractRuntime()

    contract = Contract(
        contract_id="contract-1",
        owner="alice",
        version="1.0.0",
        code_hash="abc123",
    )

    runtime.register(contract)

    result = runtime.execute(
        contract_id="contract-1",
        context=ExecutionContext(
            block_height=1,
            transaction_id="tx-1",
            caller="alice",
            network_id="ifx",
        ),
        storage=ContractStorage(),
        gas_meter=GasMeter(limit=10),
        abi=ContractABI(),
        events=EventEmitter(),
    )

    assert result.success is True
    assert result.contract_id == "contract-1"