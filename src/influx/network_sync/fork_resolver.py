from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ResolvedFork:
    """
    Represents the result of fork resolution.
    """

    height: int

    selected_root: str


class ForkResolver:
    """
    Resolves competing chain states deterministically.
    """

    def resolve(
        self,
        candidates: list[tuple[int, str]],
    ) -> ResolvedFork | None:
        """
        Select canonical chain state.
        """

        if not candidates:
            return None

        selected = sorted(
            candidates,
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )[0]

        return ResolvedFork(
            height=selected[0],
            selected_root=selected[1],
        )