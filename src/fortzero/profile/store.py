"""JSON-backed profile storage."""

from __future__ import annotations

import json
import re
from pathlib import Path

from fortzero.profile.models import PlayerProfile, utc_now_iso


class ProfileStoreError(RuntimeError):
    """Raised when profile storage fails."""


def slugify_alias(alias: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", alias.strip().lower())
    cleaned = cleaned.strip("-")
    if not cleaned:
        raise ProfileStoreError("Alias must contain at least one valid character.")
    return cleaned


class ProfileStore:
    def __init__(self, profiles_dir: Path) -> None:
        self.profiles_dir = profiles_dir

    def profile_path(self, alias: str) -> Path:
        return self.profiles_dir / f"{slugify_alias(alias)}.json"

    def list_profiles(self) -> list[PlayerProfile]:
        profiles: list[PlayerProfile] = []

        for path in sorted(self.profiles_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
            profiles.append(PlayerProfile.from_dict(raw))

        profiles.sort(key=lambda p: p.last_opened_at, reverse=True)
        return profiles

    def exists(self, alias: str) -> bool:
        return self.profile_path(alias).exists()

    def save(self, profile: PlayerProfile) -> None:
        path = self.profile_path(profile.alias)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(profile.to_dict(), handle, indent=2)

    def load(self, alias: str) -> PlayerProfile:
        path = self.profile_path(alias)
        if not path.exists():
            raise ProfileStoreError(f"Profile not found: {alias}")

        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        profile = PlayerProfile.from_dict(raw)
        profile.last_opened_at = utc_now_iso()
        self.save(profile)
        return profile
