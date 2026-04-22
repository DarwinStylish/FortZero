"""Mission runtime models for FortZero."""

from __future__ import annotations

from dataclasses import dataclass, field

from fortzero.content.models import MissionDefinition
from fortzero.profile.models import utc_now_iso


@dataclass
class ObjectiveStatus:
    id: str
    title: str
    description: str
    optional: bool
    completed: bool = False


@dataclass
class MissionRunState:
    profile_alias: str
    campaign_id: str
    mission_id: str
    status: str = "active"
    started_at: str = field(default_factory=utc_now_iso)
    ended_at: str | None = None
    objectives: list[ObjectiveStatus] = field(default_factory=list)


@dataclass(frozen=True)
class MissionLaunchContext:
    mission: MissionDefinition
    available: bool
    reason: str | None = None
