import json
from typing import Any


class Canonicalizer:
    """
    Converts runtime state into a deterministic, hash-safe structure.

    This is the ONLY valid input to hashing + consensus.
    """

    @staticmethod
    def normalize(data: Any) -> Any:
        """
        Recursively convert all structures into deterministic equivalents.
        """

        # ---- primitives ----
        if data is None:
            return None

        if isinstance(data, (str, int, float, bool)):
            return data

        # ---- dicts (SORT KEYS ALWAYS) ----
        if isinstance(data, dict):
            return {
                str(k): Canonicalizer.normalize(data[k])
                for k in sorted(data.keys(), key=lambda x: str(x))
            }

        # ---- lists (PRESERVE ORDER OR ENFORCE SORT RULE) ----
        if isinstance(data, list):
            return [
                Canonicalizer.normalize(item)
                for item in data
            ]

        # ---- sets (FORBIDDEN STRUCTURE → FORCE SORTED LIST) ----
        if isinstance(data, set):
            return sorted(
                [Canonicalizer.normalize(x) for x in data],
                key=lambda x: str(x)
            )

        # ---- fallback ----
        return str(data)

    @staticmethod
    def strip_non_deterministic_fields(state: dict) -> dict:
        """
        Remove anything that breaks determinism.
        """

        forbidden_keys = {
            "timestamp",
            "time",
            "trace",
            "logs",
            "debug",
            "replay",
            "metrics"
        }

        cleaned = {}

        for k, v in state.items():
            if k in forbidden_keys:
                continue

            if isinstance(v, dict):
                cleaned[k] = Canonicalizer.strip_non_deterministic_fields(v)
            else:
                cleaned[k] = v

        return cleaned

    @staticmethod
    def build(state: Any) -> str:
        """
        FINAL CANONICAL OUTPUT (THIS IS WHAT YOU HASH)
        """

        # 1. strip noise
        cleaned = Canonicalizer.strip_non_deterministic_fields(state)

        # 2. normalize structure
        normalized = Canonicalizer.normalize(cleaned)

        # 3. serialize deterministically
        return json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":")
        )