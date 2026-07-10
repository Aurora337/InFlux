from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json


@dataclass(slots=True)
class RPCRequest:
    """
    Represents a deterministic RPC request.
    """

    method: str

    params: dict[str, Any] = field(
        default_factory=dict
    )

    request_id: str = "0"

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize RPC request.
        """

        return {
            "request_id": self.request_id,
            "method": self.method,
            "params": self.params,
        }

    def serialize(
        self,
    ) -> str:
        """
        Serialize request to JSON.
        """

        return json.dumps(
            self.to_dict(),
            sort_keys=True,
        )


@dataclass(slots=True)
class RPCResponse:
    """
    Represents a deterministic RPC response.
    """

    request_id: str

    result: Any = None

    error: str | None = None

    def success(
        self,
    ) -> bool:
        """
        Determine response status.
        """

        return self.error is None

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize RPC response.
        """

        return {
            "request_id": self.request_id,
            "result": self.result,
            "error": self.error,
        }

    def serialize(
        self,
    ) -> str:
        """
        Serialize response to JSON.
        """

        return json.dumps(
            self.to_dict(),
            sort_keys=True,
        )