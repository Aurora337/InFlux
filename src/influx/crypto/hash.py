import hashlib
import json
from typing import Any
from dataclasses import asdict, is_dataclass

class DeterministicHasher:
    """
    Fully deterministic hashing engine for InFlux.

    Guarantees:
    - identical input → identical hash across ALL nodes
    - order-independent serialization
    - deep normalization of nested structures
    """

    @staticmethod
    def normalize(data: Any) -> Any:
        """
        Recursively convert data into deterministic structure.
        """

        if is_dataclass(data):
            return DeterministicHasher.normalize(asdict(data))

        if isinstance(data, dict):
            return {
                key: DeterministicHasher.normalize(data[key])
                for key in sorted(data.keys())
            }

        elif isinstance(data, list):
            return [
                DeterministicHasher.normalize(item)
                for item in data
            ]

        elif isinstance(data, tuple):
            return tuple(
                DeterministicHasher.normalize(item)
                for item in data
            )

        elif isinstance(data, set):
            return sorted(
                DeterministicHasher.normalize(item)
                for item in data
            )

        else:
            return data

    @staticmethod
    def serialize(data: Any) -> str:
        """
        Convert normalized structure into deterministic string.
        """
        normalized = DeterministicHasher.normalize(data)
        return json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False
        )

    @staticmethod
    def hash(data: Any) -> str:
        """
        Generate deterministic SHA-256 hash.
        """
        serialized = DeterministicHasher.serialize(data)
        return hashlib.sha256(
        serialized.encode("utf-8")
        ).hexdigest()


        return DeterministicHasher.hash(serialized)