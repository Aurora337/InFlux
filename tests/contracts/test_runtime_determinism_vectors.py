from influx.contracts.runtime import ContractRuntime
from influx.contracts.context import ExecutionContext
from influx.contracts.storage import ContractStorage
from influx.contracts.gas import GasMeter
from influx.contracts.events import EventEmitter
from influx.contracts.abi import ContractABI


from influx.contracts.contract import Contract


def create_contract():
    return Contract(
        contract_id="test_contract",
        owner="validator_001",
        version="1.0.0",
        code_hash="abc123",
    )


def create_runtime():
    runtime = ContractRuntime()

    runtime.register(
        create_contract()
    )

    return runtime


def create_context():
    return ExecutionContext(
        network_id="influx-testnet",
        block_height=1,
        transaction_id="tx_001",
        caller="validator_001",
    )


def create_environment():
    return (
        ContractStorage(),
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )


def test_same_execution_produces_same_result():
    runtime_a = create_runtime()
    runtime_b = create_runtime()

    storage_a, gas_a, abi_a, events_a = create_environment()
    storage_b, gas_b, abi_b, events_b = create_environment()

    result_a = runtime_a.execute(
        "test_contract",
        create_context(),
        storage_a,
        gas_a,
        abi_a,
        events_a,
    )

    result_b = runtime_b.execute(
        "test_contract",
        create_context(),
        storage_b,
        gas_b,
        abi_b,
        events_b,
    )

    assert result_a == result_b


def test_execution_changes_storage_deterministically():
    runtime = create_runtime()

    storage, gas, abi, events = create_environment()

    runtime.execute(
        "test_contract",
        create_context(),
        storage,
        gas,
        abi,
        events,
    )

    assert storage.get("last_transaction") == "tx_001"
    assert storage.get("last_caller") == "validator_001"
    assert storage.get("last_block") == "1"


def test_registered_contract_count():
    runtime = create_runtime()

    assert runtime.registered() == 1


def test_duplicate_contract_registration_fails():
    runtime = create_runtime()

    try:
        runtime.register(
            DummyContract()
        )
    except Exception:
        assert True
    else:
        assert False


def test_missing_contract_fails():
    runtime = ContractRuntime()

    storage, gas, abi, events = create_environment()

    try:
        runtime.execute(
            "missing",
            create_context(),
            storage,
            gas,
            abi,
            events,
        )
    except Exception:
        assert True
    else:
        assert False