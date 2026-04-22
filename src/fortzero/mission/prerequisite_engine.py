"""Mission prerequisite checks for FortZero."""

from __future__ import annotations

from fortzero.content.models import MissionDefinition
from fortzero.world.models import WorldState


class PrerequisiteEngine:
    def is_available(
        self,
        mission: MissionDefinition,
        completed_mission_ids: set[str],
        world_state: WorldState | None = None,
    ) -> tuple[bool, str | None]:
        missing = [req for req in mission.prerequisites if req not in completed_mission_ids]
        if missing:
            return False, f"Missing prerequisite missions: {', '.join(missing)}"

        if world_state is not None:
            if mission.order == 1:
                return True, None

            if mission.id not in world_state.unlocked_missions and mission.id not in completed_mission_ids:
                return False, f"Mission not yet unlocked in persistent world state: {mission.id}"

        return True, None
