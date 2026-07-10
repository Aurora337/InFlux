from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MembershipPolicy:
    """
    Defines cluster membership rules.
    """

    max_members: int = 1000

    require_validator: bool = False

    allow_storage_nodes: bool = True

    allow_archive_nodes: bool = True


    def validate_member_limit(
        self,
        current_members: int,
    ) -> bool:
        """
        Ensure cluster capacity.
        """

        return current_members < self.max_members


    def validate_roles(
        self,
        validator: bool,
        storage: bool,
        archive: bool,
    ) -> bool:
        """
        Validate node roles.
        """

        if (
            self.require_validator
            and not validator
        ):
            return False


        if (
            storage
            and not self.allow_storage_nodes
        ):
            return False


        if (
            archive
            and not self.allow_archive_nodes
        ):
            return False


        return True


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic policy snapshot.
        """

        return {
            "max_members":
                self.max_members,

            "require_validator":
                self.require_validator,

            "allow_storage_nodes":
                self.allow_storage_nodes,

            "allow_archive_nodes":
                self.allow_archive_nodes,
        }