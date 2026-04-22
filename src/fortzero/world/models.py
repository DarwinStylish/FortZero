"""World-state models for FortZero."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class WorldState:
    profile_alias: str
    completed_missions: list[str] = field(default_factory=list)
    unlocked_missions: list[str] = field(default_factory=list)
    discovered_intel: list[str] = field(default_factory=list)
    acquired_access: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, profile_alias: str, data: dict[str, Any]) -> "WorldState":
        return cls(
            profile_alias=profile_alias,
            completed_missions=list(data.get("completed_missions", [])),
            unlocked_missions=list(data.get("unlocked_missions", [])),
            discovered_intel=list(data.get("discovered_intel", [])),
            acquired_access=list(data.get("acquired_access", [])),
        )
