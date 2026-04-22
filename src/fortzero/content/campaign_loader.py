"""Campaign manifest loading for FortZero."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fortzero.content.models import CampaignDefinition, MissionDefinition
from fortzero.content.mission_loader import MissionLoader
from fortzero.content.validator import (
    ContentValidationError,
    require_list,
    require_mapping,
    require_str,
    validate_required_keys,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ContentValidationError(f"Campaign manifest not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    return require_mapping(raw, f"Campaign manifest at {path}")


class CampaignLoader:
    def __init__(self) -> None:
        self.mission_loader = MissionLoader()

    def load_campaign(self, campaign_dir: Path) -> tuple[CampaignDefinition, list[MissionDefinition]]:
        campaign_file = campaign_dir / "campaign.yaml"
        data = _load_yaml(campaign_file)

        validate_required_keys(data, ["id", "title", "description", "missions"], "campaign")

        mission_items = require_list(data["missions"], "campaign.missions")
        mission_ids: list[str] = []
        missions: list[MissionDefinition] = []

        for item in mission_items:
            mission_rel_path = require_str(item, "campaign.missions[]")
            mission_path = campaign_dir / mission_rel_path / "mission.yaml"
            mission = self.mission_loader.load(mission_path)
            missions.append(mission)
            mission_ids.append(mission.id)

        missions.sort(key=lambda m: m.order)

        campaign = CampaignDefinition(
            id=require_str(data["id"], "campaign.id"),
            title=require_str(data["title"], "campaign.title"),
            description=require_str(data["description"], "campaign.description"),
            mission_ids=mission_ids,
        )

        for mission in missions:
            if mission.campaign_id != campaign.id:
                raise ContentValidationError(
                    f"Mission '{mission.id}' campaign_id '{mission.campaign_id}' "
                    f"does not match campaign '{campaign.id}'"
                )

        return campaign, missions

    def discover_campaigns(
        self,
        campaigns_root: Path,
    ) -> list[tuple[CampaignDefinition, list[MissionDefinition]]]:
        if not campaigns_root.exists():
            return []

        loaded: list[tuple[CampaignDefinition, list[MissionDefinition]]] = []

        for campaign_dir in sorted(path for path in campaigns_root.iterdir() if path.is_dir()):
            loaded.append(self.load_campaign(campaign_dir))

        return loaded
