"""Session service for FortZero shell."""

from __future__ import annotations

from fortzero.profile.models import PlayerProfile
from fortzero.session.models import ShellSession


class SessionService:
    def start(self, profile: PlayerProfile) -> ShellSession:
        return ShellSession(profile=profile, active=True)
