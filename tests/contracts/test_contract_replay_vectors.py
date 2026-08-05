from influx.contracts.contract import Contract
from influx.contracts.context import ExecutionContext
from influx.contracts.events import EventEmitter
from influx.contracts.abi import ContractABI
from influx.contracts.gas import GasMeter
from influx.contracts.storage import ContractStorage
from influx.contracts.runtime import ContractRuntime
from influx.crypto.hash import DeterministicHasher


def create_contract():
    return Contract(
        contract_id="replay_contract",
        owner="validator_001",
        version="1.0.0",
        code_hash="hash123",
    )


def create_context():
    return ExecutionContext(
        network_id="influx-testnet",
        block_height=1,
        transaction_id="tx_replay_001",
        caller="validator_001",
    )


def create_runtime():
    runtime = ContractRuntime()
    runtime.register(create_contract())
    return runtime


def execute_contract():
    runtime = create_runtime()

    storage = ContractStorage()

    runtime.execute(
        "replay_contract",
        create_context(),
        storage,
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )

    return storage


def storage_root(storage):
    return DeterministicHasher.hash(
        storage.snapshot()
    )


def test_replay_execution_produces_same_storage():
    first = execute_contract()
    second = execute_contract()

    assert first.snapshot() == second.snapshot()


def test_replay_execution_produces_same_root():
    first = execute_contract()
    second = execute_contract()

    assert storage_root(first) == storage_root(second)


def test_replay_result_is_deterministic():
    runtime = create_runtime()

    storage_a = ContractStorage()
    storage_b = ContractStorage()

    result_a = runtime.execute(
        "replay_contract",
        create_context(),
        storage_a,
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )

    result_b = runtime.execute(
        "replay_contract",
        create_context(),
        storage_b,
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )

    assert result_a == result_b


def test_changed_transaction_changes_replay_state():
    runtime = create_runtime()

    storage_a = ContractStorage()
    storage_b = ContractStorage()

    runtime.execute(
        "replay_contract",
        create_context(),
        storage_a,
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )

    changed_context = ExecutionContext(
        network_id="influx-testnet",
        block_height=1,
        transaction_id="different_tx",
        caller="validator_001",
    )

    runtime.execute(
        "replay_contract",
        changed_context,
        storage_b,
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )

    assert storage_root(storage_a) != storage_root(storage_b)


def test_corrupted_replay_state_detected():
    storage = execute_contract()

    original_root = storage_root(storage)

    storage.put(
        "last_block",
        "999",
    )

    corrupted_root = storage_root(storage)

    assert original_root != corrupted_root