"""serialization.py

Placeholder serializers for ledger events/state.
"""

import json
from typing import Any

def serialize_event(event: Any) -> str:
    return json.dumps(event, default=str)

def deserialize_event(s: str) -> Any:
    return json.loads(s)

__all__ = ["serialize_event", "deserialize_event"]
