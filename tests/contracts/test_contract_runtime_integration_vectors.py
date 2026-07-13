from influx.contracts.contract import Contract
from influx.contracts.runtime import ContractRuntime
from influx.contracts.context import ExecutionContext
from influx.contracts.storage import ContractStorage
from influx.contracts.gas import GasMeter
from influx.contracts.abi import ContractABI
from influx.contracts.events import EventEmitter
from influx.crypto.hash import DeterministicHasher


def create_contract():
    return Contract(
        contract_id="integration_contract",
        owner="validator_001",
        version="1.0.0",
        code_hash="integration_hash",
    )


def create_context(
    tx="tx_001",
):
    return ExecutionContext(
        network_id="influx-testnet",
        block_height=1,
        transaction_id=tx,
        caller="validator_001",
    )


def create_runtime():
    runtime = ContractRuntime()

    runtime.register(
        create_contract()
    )

    return runtime


def execute(
    transaction_id="tx_001",
):
    runtime = create_runtime()

    storage = ContractStorage()

    result = runtime.execute(
        "integration_contract",
        create_context(transaction_id),
        storage,
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )

    return result, storage


def root(storage):
    return DeterministicHasher.hash(
        storage.snapshot()
    )


def test_contract_runtime_executes_successfully():
    result, _ = execute()

    assert result.success is True


def test_contract_execution_creates_state():
    _, storage = execute()

    assert storage.get(
        "last_transaction"
    ) == "tx_001"


def test_contract_execution_commitment_is_deterministic():
    _, storage_a = execute()
    _, storage_b = execute()

    assert root(storage_a) == root(storage_b)


def test_transaction_change_changes_state_root():
    _, storage_a = execute(
        "tx_001"
    )

    _, storage_b = execute(
        "tx_002"
    )

    assert root(storage_a) != root(storage_b)


def test_runtime_execution_is_replayable():
    result_a, storage_a = execute()
    result_b, storage_b = execute()

    assert result_a == result_b
    assert storage_a.snapshot() == storage_b.snapshot()