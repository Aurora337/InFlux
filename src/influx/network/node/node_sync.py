from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NodeSync:
    """
    Deterministic node synchronization tracker.
    """

    synced: bool = False

    current_height: int = 0

    target_height: int = 0


    def start(
        self,
        target_height: int,
    ) -> None:
        """
        Begin synchronization.
        """

        self.target_height = target_height
        self.synced = False


    def update(
        self,
        height: int,
    ) -> None:
        """
        Update synchronization progress.
        """

        self.current_height = height

        if self.current_height >= self.target_height:
            self.synced = True


    def reset(self) -> None:
        """
        Reset synchronization state.
        """

        self.synced = False
        self.current_height = 0
        self.target_height = 0


    def is_synced(self) -> bool:
        """
        Return synchronization status.
        """

        return self.synced