"""Objective tracking for FortZero missions."""

from __future__ import annotations

from fortzero.content.models import MissionDefinition
from fortzero.mission.models import MissionRunState, ObjectiveStatus


class ObjectiveEngine:
    def initialize_run_state(
        self,
        profile_alias: str,
        mission: MissionDefinition,
    ) -> MissionRunState:
        objectives = [
            ObjectiveStatus(
                id=obj.id,
                title=obj.title,
                description=obj.description,
                optional=obj.optional,
            )
            for obj in mission.objectives
        ]
        return MissionRunState(
            profile_alias=profile_alias,
            campaign_id=mission.campaign_id,
            mission_id=mission.id,
            objectives=objectives,
        )

    def complete_objective(
        self,
        run_state: MissionRunState,
        objective_id: str,
    ) -> tuple[bool, bool]:
        for objective in run_state.objectives:
            if objective.id == objective_id:
                already_completed = objective.completed
                objective.completed = True
                return True, already_completed
        return False, False

    def required_objectives_completed(self, run_state: MissionRunState) -> bool:
        required = [obj for obj in run_state.objectives if not obj.optional]
        return all(obj.completed for obj in required)
