"""GhostWatch models for FortZero."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from fortzero.profile.models import utc_now_iso


@dataclass
class GhostWatchState:
    mission_run_id: int
    profile_alias: str
    mission_id: str
    suspicion_score: int = 0
    posture: str = "calm"
    signals: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
