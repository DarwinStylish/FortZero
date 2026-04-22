"""Application state manager for FortZero."""

from __future__ import annotations

from pathlib import Path

from fortzero.data.event_repository import EventRepository
from fortzero.data.ghostwatch_repository import GhostWatchRepository
from fortzero.data.mission_run_repository import MissionRunRepository
from fortzero.data.profile_repository import ProfileRepository
from fortzero.data.session_repository import SessionRepository
from fortzero.events.bus import EventBus
from fortzero.profile.models import PlayerProfile
from fortzero.world.world_service import WorldService


class StateManager:
    def __init__(self, db_file: Path, event_bus: EventBus | None = None) -> None:
        self.profile_repository = ProfileRepository(db_file)
        self.session_repository = SessionRepository(db_file)
        self.mission_run_repository = MissionRunRepository(db_file)
        self.ghostwatch_repository = GhostWatchRepository(db_file)
        self.event_repository = EventRepository(db_file)
        self.world_service = WorldService(db_file)
        self.event_bus = event_bus

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
