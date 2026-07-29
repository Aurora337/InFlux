"""
Example counter smart contract.

Demonstrates a simple stateful contract with
increment, decrement, and get_count functions.
"""

from __future__ import annotations

from influx.contracts.engine import FunctionHandler
from influx.contracts.contract import Contract


def counter_increment(*args, _storage, _gas, **_kwargs) -> str:
    """
    Increment the counter by 1 or by a specified amount.
    """

    increment_by = int(args[0]) if args else 1
    _gas.consume(10)

    current = int(_storage.get("count", "0"))
    new_value = current + increment_by

    _storage.put("count", str(new_value))
    _storage.put("last_action", "increment")
    _storage.put("last_value", str(increment_by))

    return str(new_value)


def counter_decrement(*args, _storage, _gas, **_kwargs) -> str:
    """
    Decrement the counter by 1 or by a specified amount.
    """

    decrement_by = int(args[0]) if args else 1
    _gas.consume(10)

    current = int(_storage.get("count", "0"))
    new_value = max(0, current - decrement_by)

    _storage.put("count", str(new_value))
    _storage.put("last_action", "decrement")
    _storage.put("last_value", str(decrement_by))

    return str(new_value)


def counter_get_count(*args, _storage, _gas, **_kwargs) -> str:
    """
    Return the current counter value.
    """

    _gas.consume(5)

    return _storage.get("count", "0")


def counter_reset(*args, _storage, _gas, **_kwargs) -> str:
    """
    Reset the counter to zero.
    """

    _gas.consume(5)

    _storage.put("count", "0")
    _storage.put("last_action", "reset")

    return "0"


def create_counter_contract(
    contract_id: str = "counter",
    owner: str = "system",
    version: str = "1.0.0",
    code_hash: str = "0xcounter_v1",
) -> tuple[Contract, list[FunctionHandler]]:
    """
    Create a counter contract with its function handlers.
    """

    contract = Contract(
        contract_id=contract_id,
        owner=owner,
        version=version,
        code_hash=code_hash,
    )

    handlers = [
        FunctionHandler(
            name="increment",
            handler=counter_increment,
            gas_cost=10,
        ),
        FunctionHandler(
            name="decrement",
            handler=counter_decrement,
            gas_cost=10,
        ),
        FunctionHandler(
            name="get_count",
            handler=counter_get_count,
            gas_cost=5,
        ),
        FunctionHandler(
            name="reset",
            handler=counter_reset,
            gas_cost=5,
        ),
    ]

    return contract, handlers