"""Session models for FortZero."""

from __future__ import annotations

from dataclasses import dataclass

from fortzero.profile.models import PlayerProfile


@dataclass
class ShellSession:
    profile: PlayerProfile
    session_id: int
    active: bool = True
