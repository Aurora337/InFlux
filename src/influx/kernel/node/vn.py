class ValidatorNode:
    def __init__(self, node_id: str):
        self.node_id = node_id

    def validate_hash(
        self,
        local_hash: str,
        network_hash: str
    ) -> bool:

        return local_hash == network_hash

    def status(self) -> dict:

        return {
            "id": self.node_id,
            "role": "VN"
        }
