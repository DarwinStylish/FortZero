"""Mission prerequisite checks for FortZero."""

from __future__ import annotations

from fortzero.content.models import MissionDefinition


class PrerequisiteEngine:
    def is_available(
        self,
        mission: MissionDefinition,
        completed_mission_ids: set[str],
    ) -> tuple[bool, str | None]:
        missing = [req for req in mission.prerequisites if req not in completed_mission_ids]
        if missing:
            return False, f"Missing prerequisite missions: {', '.join(missing)}"
        return True, None
