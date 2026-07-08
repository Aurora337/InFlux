import json
from typing import Any

def canonicalize(obj: Any) -> str:
    """
    Deep deterministic serialization for ALL consensus objects.
    """

    return json.dumps(
        _normalize(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def _normalize(obj: Any) -> Any:
    # primitives
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # dict → sorted keys ALWAYS
    if isinstance(obj, dict):
        return {k: _normalize(obj[k]) for k in sorted(obj.keys())}

    # list → sort by deterministic hash of element
    if isinstance(obj, list):
        normalized = [_normalize(x) for x in obj]

        # IMPORTANT: enforce deterministic ordering
        return sorted(
            normalized,
            key=lambda x: json.dumps(x, sort_keys=True)
        )

    return str(obj)