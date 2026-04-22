"""GhostWatch MVP engine for FortZero."""

from __future__ import annotations

from fortzero.data.ghostwatch_repository import GhostWatchRepository
from fortzero.events.bus import EventBus
from fortzero.events.models import DomainEvent, EventTypes
from fortzero.ghostwatch.detectors import GhostWatchDetectors
from fortzero.ghostwatch.models import GhostWatchState
from fortzero.ghostwatch.responders import GhostWatchResponders
from fortzero.ghostwatch.state_machine import GhostWatchStateMachine


class GhostWatchEngine:
    def __init__(self, event_bus: EventBus, repository: GhostWatchRepository) -> None:
        self.event_bus = event_bus
        self.repository = repository
        self.detectors = GhostWatchDetectors()
        self.state_machine = GhostWatchStateMachine()
        self.responders = GhostWatchResponders()

    def initialize_for_run(self, mission_run_id: int, profile_alias: str, mission_id: str) -> GhostWatchState:
        state = GhostWatchState(
            mission_run_id=mission_run_id,
            profile_alias=profile_alias,
            mission_id=mission_id,
        )
        self.repository.save(state)
        return state

    def current_state(self, mission_run_id: int) -> GhostWatchState | None:
        return self.repository.load(mission_run_id)

    def handle_event(self, event: DomainEvent) -> None:
        mission_run_id = event.payload.get("run_id")
        if not isinstance(mission_run_id, int):
            return

        state = self.repository.load(mission_run_id)
        if state is None:
            return

        signal = self.detectors.signal_for_event(event)
        if signal is None:
            return

        reason, score_delta = signal
        old_posture = state.posture

        state.suspicion_score += score_delta
        state.signals.append(reason)
        state.posture = self.state_machine.posture_for_score(state.suspicion_score)
        self.repository.save(state)

        if state.posture != old_posture:
            self.event_bus.publish(
                DomainEvent(
                    event_type=EventTypes.GHOSTWATCH_POSTURE_CHANGED,
                    source="ghostwatch.engine",
                    profile_alias=state.profile_alias,
                    mission_id=state.mission_id,
                    payload={
                        "run_id": state.mission_run_id,
                        "old_posture": old_posture,
                        "new_posture": state.posture,
                        "message": self.responders.message_for_posture(state.posture),
                        "reason": reason,
                        "score_delta": score_delta,
                        "suspicion_score": state.suspicion_score,
                    },
                )
            )
