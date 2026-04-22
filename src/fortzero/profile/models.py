"""Profile models for FortZero."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass
class PlayerProfile:
    alias: str
    preferred_mode: str = "agent"
    created_at: str = field(default_factory=utc_now_iso)
    last_opened_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlayerProfile":
        return cls(
            alias=str(data["alias"]),
            preferred_mode=str(data.get("preferred_mode", "agent")),
            created_at=str(data.get("created_at", utc_now_iso())),
            last_opened_at=str(data.get("last_opened_at", utc_now_iso())),
        )
