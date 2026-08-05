from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HistoryIndexEntry:
    """
    Index entry for historical state lookup.
    """

    height: int

    root_hash: str


class HistoryIndex:
    """
    Provides deterministic historical indexing.
    """

    def __init__(
        self,
    ) -> None:

        self._entries: dict[
            int,
            HistoryIndexEntry,
        ] = {}

    def add(
        self,
        height: int,
        root_hash: str,
    ) -> HistoryIndexEntry:
        """
        Add history index entry.
        """

        entry = HistoryIndexEntry(
            height=height,
            root_hash=root_hash,
        )

        self._entries[
            height
        ] = entry

        return entry

    def get(
        self,
        height: int,
    ) -> HistoryIndexEntry | None:
        """
        Retrieve indexed entry.
        """

        return self._entries.get(
            height
        )

    def contains(
        self,
        height: int,
    ) -> bool:
        """
        Check if height exists.
        """

        return height in self._entries

    def heights(
        self,
    ) -> list[int]:
        """
        Return ordered index heights.
        """

        return sorted(
            self._entries.keys()
        )