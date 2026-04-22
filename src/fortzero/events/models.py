"""Event models for FortZero."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from fortzero.profile.models import utc_now_iso


@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: str = field(default_factory=utc_now_iso)
    mission_id: str | None = None
    profile_alias: str | None = None
    session_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventTypes:
    APP_BOOTSTRAPPED = "app.bootstrapped"
    PROFILE_CREATED = "profile.created"
    PROFILE_LOADED = "profile.loaded"
    SESSION_STARTED = "session.started"
    SESSION_ENDED = "session.ended"
    USER_EXITED = "shell.user_exited"
    MENU_OPENED = "shell.menu_opened"
    MENU_SELECTED = "shell.menu_selected"

    MISSION_STARTED = "mission.started"
    MISSION_COMPLETED = "mission.completed"
    MISSION_BLOCKED = "mission.blocked"
    OBJECTIVE_COMPLETED = "objective.completed"

    GHOSTWATCH_SIGNAL = "ghostwatch.signal"
    GHOSTWATCH_POSTURE_CHANGED = "ghostwatch.posture_changed"

    RUNTIME_INITIALIZED = "runtime.initialized"
    RUNTIME_ACTION = "runtime.action"
    RUNTIME_STATE_CHANGED = "runtime.state_changed"
