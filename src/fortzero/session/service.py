"""Session service for FortZero shell."""

from __future__ import annotations

from fortzero.profile.models import PlayerProfile
from fortzero.session.models import ShellSession
from fortzero.state.state_manager import StateManager


class SessionService:
    def __init__(self, state_manager: StateManager) -> None:
        self.state_manager = state_manager

    def start(self, profile: PlayerProfile) -> ShellSession:
        session_id = self.state_manager.start_session(profile.alias)
        return ShellSession(profile=profile, session_id=session_id, active=True)

    def end(self, session: ShellSession) -> None:
        self.state_manager.end_session(session.session_id)
        session.active = False
