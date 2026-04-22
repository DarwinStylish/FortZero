"""Application state manager for FortZero."""

from __future__ import annotations

from pathlib import Path

from fortzero.data.profile_repository import ProfileRepository
from fortzero.data.session_repository import SessionRepository
from fortzero.profile.models import PlayerProfile


class StateManager:
    def __init__(self, db_file: Path) -> None:
        self.profile_repository = ProfileRepository(db_file)
        self.session_repository = SessionRepository(db_file)

    def list_profiles(self) -> list[PlayerProfile]:
        return self.profile_repository.list_profiles()

    def create_or_update_profile(self, profile: PlayerProfile) -> None:
        self.profile_repository.save(profile)

    def load_profile(self, alias: str) -> PlayerProfile:
        return self.profile_repository.load(alias)

    def start_session(self, profile_alias: str) -> int:
        return self.session_repository.start_session(profile_alias)

    def end_session(self, session_id: int) -> None:
        self.session_repository.end_session(session_id)
