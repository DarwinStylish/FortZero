"""Content models for FortZero campaigns and missions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModeConfig:
    hints_enabled: bool
    ghostwatch_sensitivity: str


@dataclass(frozen=True)
class ObjectiveDefinition:
    id: str
    title: str
    description: str
    optional: bool = False


@dataclass(frozen=True)
class MissionDefinition:
    id: str
    title: str
    briefing: str
    campaign_id: str
    order: int
    prerequisites: list[str] = field(default_factory=list)
    objectives: list[ObjectiveDefinition] = field(default_factory=list)
    mode_agent: ModeConfig = field(default_factory=lambda: ModeConfig(True, "normal"))
    mode_spectre: ModeConfig = field(default_factory=lambda: ModeConfig(False, "high"))


@dataclass(frozen=True)
class CampaignDefinition:
    id: str
    title: str
    description: str
    mission_ids: list[str]
