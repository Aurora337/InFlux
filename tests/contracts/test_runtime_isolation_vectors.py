from influx.contracts.contract import Contract
from influx.contracts.context import ExecutionContext
from influx.contracts.events import EventEmitter
from influx.contracts.gas import GasMeter
from influx.contracts.runtime import ContractRuntime
from influx.contracts.storage import ContractStorage
from influx.contracts.abi import ContractABI


def create_context():
    return ExecutionContext(
        block_height=1,
        transaction_id="tx_isolation_001",
        caller="validator_isolation",
        network_id="testnet",
    )


def create_contract(contract_id: str):
    return Contract(
        contract_id=contract_id,
        owner="owner_001",
        version="1.0",
        code_hash=f"hash_{contract_id}",
    )


def create_environment():
    return (
        ContractStorage(),
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )


def test_storage_isolation_between_contracts():
    runtime = ContractRuntime()

    contract_a = create_contract("contract_a")
    contract_b = create_contract("contract_b")

    runtime.register(contract_a)
    runtime.register(contract_b)

    storage_a, gas_a, abi_a, events_a = create_environment()
    storage_b, gas_b, abi_b, events_b = create_environment()

    runtime.execute(
        "contract_a",
        create_context(),
        storage_a,
        gas_a,
        abi_a,
        events_a,
    )

    assert storage_a.get("last_transaction") == "tx_isolation_001"
    assert storage_b.get("last_transaction") is None


def test_execution_context_isolation():
    runtime = ContractRuntime()

    runtime.register(
        create_contract("context_contract")
    )

    storage, gas, abi, events = create_environment()

    context = ExecutionContext(
        block_height=42,
        transaction_id="unique_tx",
        caller="unique_caller",
        network_id="isolated_network",
    )

    runtime.execute(
        "context_contract",
        context,
        storage,
        gas,
        abi,
        events,
    )

    assert storage.get("last_transaction") == "unique_tx"
    assert storage.get("last_caller") == "unique_caller"
    assert storage.get("last_block") == "42"


def test_gas_meter_isolation():
    gas_a = GasMeter(limit=100)
    gas_b = GasMeter(limit=100)

    gas_a.consume(10)

    assert gas_a.remaining() == 90
    assert gas_b.remaining() == 100


def test_event_isolation_between_contracts():
    events_a = EventEmitter()
    events_b = EventEmitter()

    from influx.contracts.events import ContractEvent

    events_a.emit(
        ContractEvent(
            event_name="ContractExecuted",
            contract_id="contract_a",
            payload={"contract": "contract_a"},
        )
    )

    assert events_a.count() == 1
    assert events_b.count() == 0

def test_contract_identity_isolation():
    contract_a = create_contract("contract_a")
    contract_b = create_contract("contract_b")

    assert contract_a.contract_id != contract_b.contract_id
    assert contract_a.code_hash != contract_b.code_hash