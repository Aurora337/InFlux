from __future__ import annotations

import json

from influx.network.message import NetworkMessage


class MessageSerializer:
    """
    Deterministic serializer for NetworkMessage objects.
    """

    @staticmethod
    def serialize(message: NetworkMessage) -> str:
        return json.dumps(
            {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "epoch": message.epoch,
                "ctor_slot": message.ctor_slot,
                "timestamp": message.timestamp,
                "message_type": message.message_type,
                "payload": message.payload,
                "state_hash": message.state_hash,
                "signature": message.signature,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def deserialize(data: str) -> NetworkMessage:
        obj = json.loads(data)

        return NetworkMessage(
            message_id=obj["message_id"],
            sender_id=obj["sender_id"],
            receiver_id=obj["receiver_id"],
            epoch=obj["epoch"],
            ctor_slot=obj["ctor_slot"],
            timestamp=obj["timestamp"],
            message_type=obj["message_type"],
            payload=obj["payload"],
            state_hash=obj["state_hash"],
            signature=obj["signature"],
        )