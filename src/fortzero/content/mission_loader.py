"""Mission manifest loading for FortZero."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fortzero.content.models import MissionDefinition, ModeConfig, ObjectiveDefinition
from fortzero.content.validator import (
    ContentValidationError,
    require_bool,
    require_list,
    require_mapping,
    require_str,
    validate_required_keys,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ContentValidationError(f"Mission manifest not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    return require_mapping(raw, f"Mission manifest at {path}")


def _parse_mode_config(data: dict[str, Any], context: str) -> ModeConfig:
    validate_required_keys(data, ["hints_enabled", "ghostwatch_sensitivity"], context)
    return ModeConfig(
        hints_enabled=require_bool(data["hints_enabled"], f"{context}.hints_enabled"),
        ghostwatch_sensitivity=require_str(
            data["ghostwatch_sensitivity"],
            f"{context}.ghostwatch_sensitivity",
        ),
    )


def _parse_objectives(items: list[Any]) -> list[ObjectiveDefinition]:
    objectives: list[ObjectiveDefinition] = []

    for index, item in enumerate(items, start=1):
        obj = require_mapping(item, f"objective[{index}]")
        validate_required_keys(obj, ["id", "title", "description"], f"objective[{index}]")
        objectives.append(
            ObjectiveDefinition(
                id=require_str(obj["id"], f"objective[{index}].id"),
                title=require_str(obj["title"], f"objective[{index}].title"),
                description=require_str(obj["description"], f"objective[{index}].description"),
                optional=bool(obj.get("optional", False)),
            )
        )

    return objectives


class MissionLoader:
    def load(self, manifest_path: Path) -> MissionDefinition:
        data = _load_yaml(manifest_path)
        validate_required_keys(
            data,
            [
                "id",
                "title",
                "briefing",
                "campaign_id",
                "order",
                "objectives",
                "modes",
            ],
            "mission",
        )

        modes = require_mapping(data["modes"], "mission.modes")
        validate_required_keys(modes, ["agent", "spectre"], "mission.modes")

        order = data["order"]
        if not isinstance(order, int):
            raise ContentValidationError("mission.order must be an integer")

        prerequisites_raw = data.get("prerequisites", [])
        prerequisites = [
            require_str(item, "mission.prerequisites[]")
            for item in require_list(prerequisites_raw, "mission.prerequisites")
        ]

        objectives = _parse_objectives(require_list(data["objectives"], "mission.objectives"))

        return MissionDefinition(
            id=require_str(data["id"], "mission.id"),
            title=require_str(data["title"], "mission.title"),
            briefing=require_str(data["briefing"], "mission.briefing"),
            campaign_id=require_str(data["campaign_id"], "mission.campaign_id"),
            order=order,
            prerequisites=prerequisites,
            objectives=objectives,
            mode_agent=_parse_mode_config(
                require_mapping(modes["agent"], "mission.modes.agent"),
                "mission.modes.agent",
            ),
            mode_spectre=_parse_mode_config(
                require_mapping(modes["spectre"], "mission.modes.spectre"),
                "mission.modes.spectre",
            ),
        )
