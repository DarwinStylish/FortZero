"""Profile service for shell interactions."""

from __future__ import annotations

from fortzero.profile.models import PlayerProfile
from fortzero.profile.store import ProfileStore


class ProfileService:
    def __init__(self, store: ProfileStore) -> None:
        self.store = store

    def list_profiles(self) -> list[PlayerProfile]:
        return self.store.list_profiles()

    def create_profile(self, alias: str, preferred_mode: str = "agent") -> PlayerProfile:
        profile = PlayerProfile(alias=alias.strip(), preferred_mode=preferred_mode.strip().lower())
        self.store.save(profile)
        return profile

    def load_profile(self, alias: str) -> PlayerProfile:
        return self.store.load(alias)
