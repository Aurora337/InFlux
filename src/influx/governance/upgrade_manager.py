from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UpgradeRecord:
    """
    Represents activated protocol upgrade.
    """

    version: str

    activated: bool = False


class UpgradeManager:
    """
    Handles deterministic protocol upgrades.
    """

    def __init__(
        self,
    ) -> None:

        self._upgrades: list[UpgradeRecord] = []

    def schedule(
        self,
        version: str,
    ) -> UpgradeRecord:
        """
        Schedule protocol upgrade.
        """

        record = UpgradeRecord(
            version=version,
        )

        self._upgrades.append(
            record
        )

        return record

    def activate(
        self,
        version: str,
    ) -> bool:
        """
        Activate scheduled upgrade.
        """

        for upgrade in self._upgrades:

            if upgrade.version == version:

                upgrade.activated = True

                return True

        return False

    def history(
        self,
    ) -> list[UpgradeRecord]:
        """
        Return upgrade history.
        """

        return list(
            self._upgrades
        )