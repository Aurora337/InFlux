class ValidatorNode:
    """Verification Node (VN): verifies events and hashes only."""

    def __init__(self, node_id: str):
        self.node_id = node_id

    def validate_hash(self, local_hash: str, network_hash: str) -> bool:
        return local_hash == network_hash

    def verify_event(self, event_hash: str, expected_hash: str) -> bool:
        return event_hash == expected_hash

    def reproduce(self, *_args, **_kwargs):
        raise PermissionError("VN cannot perform reproduction operations")

    def mutate_reserve_supply(self, *_args, **_kwargs):
        raise PermissionError("VN cannot mutate reserve supply")

    def create_circulation_transfer(self, *_args, **_kwargs):
        raise PermissionError("VN cannot create circulation transfers")

    def status(self) -> dict:
        return {"id": self.node_id, "role": "VN"}
