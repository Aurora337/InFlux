from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HistoryMetrics:
    """
    Tracks historical state activity.
    """

    states_recorded: int = 0

    replay_attempts: int = 0

    successful_replays: int = 0

    failed_replays: int = 0

    queries: int = 0

    root_verifications: int = 0

    successful_verifications: int = 0

    failed_verifications: int = 0

    def record_state(
        self,
    ) -> None:
        """
        Record historical state creation.
        """

        self.states_recorded += 1

    def record_replay(
        self,
        success: bool,
    ) -> None:
        """
        Record replay attempt.
        """

        self.replay_attempts += 1

        if success:
            self.successful_replays += 1
        else:
            self.failed_replays += 1

    def record_query(
        self,
    ) -> None:
        """
        Record historical query.
        """

        self.queries += 1

    def record_verification(
        self,
        success: bool,
    ) -> None:
        """
        Record root verification.
        """

        self.root_verifications += 1

        if success:
            self.successful_verifications += 1
        else:
            self.failed_verifications += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "states_recorded":
                self.states_recorded,

            "replay_attempts":
                self.replay_attempts,

            "successful_replays":
                self.successful_replays,

            "failed_replays":
                self.failed_replays,

            "queries":
                self.queries,

            "root_verifications":
                self.root_verifications,

            "successful_verifications":
                self.successful_verifications,

            "failed_verifications":
                self.failed_verifications,
        }