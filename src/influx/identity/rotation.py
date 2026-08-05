from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class KeyRotation:
    """
    Represents a key transition event.
    """

    identity_id: str

    old_key: str

    new_key: str

    timestamp: int


class RotationManager:
    """
    Manages identity key rotations.
    """

    def __init__(
        self,
    ) -> None:

        self._history: list[KeyRotation] = []

    def rotate(
        self,
        identity_id: str,
        old_key: str,
        new_key: str,
        timestamp: int,
    ) -> KeyRotation:
        """
        Create key rotation record.
        """

        rotation = KeyRotation(
            identity_id=identity_id,
            old_key=old_key,
            new_key=new_key,
            timestamp=timestamp,
        )

        self._history.append(
            rotation
        )

        return rotation

    def history(
        self,
    ) -> list[KeyRotation]:
        """
        Return rotation history.
        """

        return list(
            self._history
        )