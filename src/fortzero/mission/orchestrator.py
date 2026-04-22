"""Mission orchestration for FortZero."""

from __future__ import annotations

from fortzero.content.models import MissionDefinition
from fortzero.events.bus import EventBus
from fortzero.events.models import DomainEvent, EventTypes
from fortzero.mission.models import MissionLaunchContext, MissionRunState
from fortzero.mission.objective_engine import ObjectiveEngine
from fortzero.mission.prerequisite_engine import PrerequisiteEngine
from fortzero.profile.models import utc_now_iso
from fortzero.data.mission_run_repository import MissionRunRepository


class MissionOrchestrator:
    def __init__(
        self,
        event_bus: EventBus,
        mission_run_repository: MissionRunRepository,
    ) -> None:
        self.event_bus = event_bus
        self.mission_run_repository = mission_run_repository
        self.prerequisite_engine = PrerequisiteEngine()
        self.objective_engine = ObjectiveEngine()

    def launch_context(
        self,
        profile_alias: str,
        mission: MissionDefinition,
    ) -> MissionLaunchContext:
        completed = self.mission_run_repository.completed_mission_ids(
            profile_alias=profile_alias,
            campaign_id=mission.campaign_id,
        )
        available, reason = self.prerequisite_engine.is_available(mission, completed)
        return MissionLaunchContext(mission=mission, available=available, reason=reason)

    def start_run(self, profile_alias: str, mission: MissionDefinition) -> tuple[int, MissionRunState]:
        run_state = self.objective_engine.initialize_run_state(profile_alias, mission)
        run_id = self.mission_run_repository.create_run(run_state)

        self.event_bus.publish(
            DomainEvent(
                event_type=EventTypes.MISSION_STARTED,
                source="mission.orchestrator",
                profile_alias=profile_alias,
                mission_id=mission.id,
                payload={"campaign_id": mission.campaign_id, "run_id": run_id},
            )
        )
        return run_id, run_state

    def complete_objective(self, run_id: int, run_state: MissionRunState, objective_id: str) -> bool:
        changed = self.objective_engine.complete_objective(run_state, objective_id)
        if not changed:
            return False

        self.mission_run_repository.update_run(run_id, run_state)

        self.event_bus.publish(
            DomainEvent(
                event_type=EventTypes.OBJECTIVE_COMPLETED,
                source="mission.orchestrator",
                profile_alias=run_state.profile_alias,
                mission_id=run_state.mission_id,
                payload={"run_id": run_id, "objective_id": objective_id},
            )
        )
        return True

    def finalize_if_complete(self, run_id: int, run_state: MissionRunState) -> bool:
        if not self.objective_engine.required_objectives_completed(run_state):
            self.mission_run_repository.update_run(run_id, run_state)
            return False

        run_state.status = "completed"
        run_state.ended_at = utc_now_iso()
        self.mission_run_repository.update_run(run_id, run_state)

        self.event_bus.publish(
            DomainEvent(
                event_type=EventTypes.MISSION_COMPLETED,
                source="mission.orchestrator",
                profile_alias=run_state.profile_alias,
                mission_id=run_state.mission_id,
                payload={"run_id": run_id, "status": run_state.status},
            )
        )
        return True
