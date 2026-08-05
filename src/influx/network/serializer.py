from __future__ import annotations

import json

from influx.network.message import NetworkMessage


class MessageSerializer:
    """
    Deterministic serializer for NetworkMessage objects.
    """

    @staticmethod
    def serialize(message: NetworkMessage) -> str:
        """
        Serialize a NetworkMessage into a deterministic JSON string.
        """

        return json.dumps(
            {
                "message_id": message.message_id,
                "message_type": message.message_type,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "epoch": message.epoch,
                "slot": message.slot,
                "timestamp": message.timestamp,
                "payload": message.payload,
                "state_hash": message.state_hash,
                "signature": message.signature,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def deserialize(data: str) -> NetworkMessage:
        """
        Deserialize a deterministic JSON string into a NetworkMessage.
        """

        obj = json.loads(data)

        return NetworkMessage(
            message_id=obj["message_id"],
            message_type=obj["message_type"],
            sender_id=obj["sender_id"],
            receiver_id=obj["receiver_id"],
            epoch=obj["epoch"],
            slot=obj["slot"],
            timestamp=obj["timestamp"],
            payload=obj["payload"],
            state_hash=obj.get("state_hash", ""),
            signature=obj.get("signature", ""),
        )