import json


def serialize_state(state) -> bytes:
    return json.dumps(
        state.to_dict(),
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")
