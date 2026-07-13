from __future__ import annotations

import json
from typing import Any


class ContractSerializer:
    """
    Deterministic serializer for contract metadata.
    """

    @staticmethod
    def serialize(data: dict[str, Any]) -> str:
        """
        Serialize metadata deterministically.
        """
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def deserialize(payload: str) -> dict[str, Any]:
        """
        Deserialize metadata.
        """
        return json.loads(payload)