"""Profile service for shell interactions."""

from __future__ import annotations

from fortzero.profile.models import PlayerProfile
from fortzero.state.state_manager import StateManager


class ProfileService:
    def __init__(self, state_manager: StateManager) -> None:
        self.state_manager = state_manager

    def list_profiles(self) -> list[PlayerProfile]:
        return self.state_manager.list_profiles()

    def create_profile(self, alias: str, preferred_mode: str = "agent") -> PlayerProfile:
        profile = PlayerProfile(alias=alias.strip(), preferred_mode=preferred_mode.strip().lower())
        self.state_manager.create_or_update_profile(profile)
        return profile

    def load_profile(self, alias: str) -> PlayerProfile:
        return self.state_manager.load_profile(alias)
