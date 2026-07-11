from __future__ import annotations

from dataclasses import dataclass

from .node import TestnetNode

from .exceptions import NodeError


@dataclass(slots=True)
class ValidatorState:
    """
    Validator lifecycle state.
    """

    node_id: str

    active: bool = False


class ValidatorManager:
    """
    Validator lifecycle controller.
    """

    def activate(
        self,
        node: TestnetNode,
    ) -> ValidatorState:
        """
        Activate validator node.
        """

        if not node.validator:
            raise NodeError(
                "node is not a validator"
            )

        node.online = True

        return ValidatorState(
            node_id=node.node_id,
            active=True,
        )

    def deactivate(
        self,
        state: ValidatorState,
    ) -> None:
        """
        Deactivate validator.
        """

        state.active = False