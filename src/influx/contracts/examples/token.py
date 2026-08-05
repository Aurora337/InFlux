"""
Example ERC20-like token smart contract.

Demonstrates a fungible token with balances,
transfer, and approval functionality.
"""

from __future__ import annotations

from influx.contracts.engine import FunctionHandler
from influx.contracts.contract import Contract


def token_total_supply(*args, _storage, _gas, **_kwargs) -> str:
    """Return the total token supply."""
    _gas.consume(5)
    return _storage.get("total_supply", "0")


def token_balance_of(*args, _storage, _gas, **_kwargs) -> str:
    """Return the balance of a given address."""
    _gas.consume(10)
    owner = args[0] if args else "0x0"
    return _storage.get(f"balance_{owner}", "0")


def token_transfer(*args, _storage, _context, _gas, _events, **_kwargs) -> str:
    """Transfer tokens from caller to recipient."""
    _gas.consume(20)

    if len(args) < 2:
        return "error: insufficient arguments"

    to = args[0]
    amount = int(args[1])
    caller = _context.caller

    sender_balance = int(_storage.get(f"balance_{caller}", "0"))
    if sender_balance < amount:
        return "error: insufficient balance"

    receiver_balance = int(_storage.get(f"balance_{to}", "0"))

    _storage.put(f"balance_{caller}", str(sender_balance - amount))
    _storage.put(f"balance_{to}", str(receiver_balance + amount))
    _storage.put("last_transfer_from", caller)
    _storage.put("last_transfer_to", to)

    _events.emit(
        type("Event", (), {"event_name": "Transfer", "contract_id": _storage.get("contract_id", "token"), "payload": {"from": caller, "to": to, "amount": amount}})()
    )

    return "success"


def token_approve(*args, _storage, _context, _gas, **_kwargs) -> str:
    """Approve spender to spend tokens on behalf of caller."""
    _gas.consume(15)

    if len(args) < 2:
        return "error: insufficient arguments"

    spender = args[0]
    amount = int(args[1])
    caller = _context.caller

    _storage.put(f"allowance_{caller}_{spender}", str(amount))
    _storage.put("last_approval_owner", caller)
    _storage.put("last_approval_spender", spender)

    return "success"


def token_allowance(*args, _storage, _gas, **_kwargs) -> str:
    """Return the allowance for owner/spender pair."""
    _gas.consume(10)

    if len(args) < 2:
        return "0"

    owner = args[0]
    spender = args[1]

    return _storage.get(f"allowance_{owner}_{spender}", "0")


def token_transfer_from(*args, _storage, _context, _gas, **_kwargs) -> str:
    """Transfer tokens using an allowance."""
    _gas.consume(25)

    if len(args) < 3:
        return "error: insufficient arguments"

    sender = args[0]
    recipient = args[1]
    amount = int(args[2])
    caller = _context.caller

    current_allowance = int(_storage.get(f"allowance_{sender}_{caller}", "0"))
    if current_allowance < amount:
        return "error: insufficient allowance"

    sender_balance = int(_storage.get(f"balance_{sender}", "0"))
    if sender_balance < amount:
        return "error: insufficient balance"

    receiver_balance = int(_storage.get(f"balance_{recipient}", "0"))

    _storage.put(f"allowance_{sender}_{caller}", str(current_allowance - amount))
    _storage.put(f"balance_{sender}", str(sender_balance - amount))
    _storage.put(f"balance_{recipient}", str(receiver_balance + amount))

    return "success"


def create_token_contract(
    contract_id: str = "token",
    owner: str = "system",
    version: str = "1.0.0",
    code_hash: str = "0xtoken_v1",
    initial_supply: int = 1000000,
) -> tuple[Contract, list[FunctionHandler], dict[str, str]]:
    """
    Create a token contract with initial state.
    """

    contract = Contract(
        contract_id=contract_id,
        owner=owner,
        version=version,
        code_hash=code_hash,
    )

    handlers = [
        FunctionHandler(name="total_supply", handler=token_total_supply, gas_cost=5),
        FunctionHandler(name="balance_of", handler=token_balance_of, gas_cost=10),
        FunctionHandler(name="transfer", handler=token_transfer, gas_cost=20),
        FunctionHandler(name="approve", handler=token_approve, gas_cost=15),
        FunctionHandler(name="allowance", handler=token_allowance, gas_cost=10),
        FunctionHandler(name="transfer_from", handler=token_transfer_from, gas_cost=25),
    ]

    initial_state = {
        "total_supply": str(initial_supply),
        f"balance_{owner}": str(initial_supply),
        "contract_id": contract_id,
    }

    return contract, handlers, initial_state
