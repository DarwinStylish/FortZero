"""Runtime engine for FortZero target environments."""

from __future__ import annotations

from fortzero.data.runtime_repository import RuntimeRepository
from fortzero.events.bus import EventBus
from fortzero.events.models import DomainEvent, EventTypes
from fortzero.runtime.environment_factory import EnvironmentFactory
from fortzero.runtime.models import RuntimeState
from fortzero.runtime.runtime_actions import RuntimeActions


class RuntimeEngine:
    def __init__(self, event_bus: EventBus, repository: RuntimeRepository) -> None:
        self.event_bus = event_bus
        self.repository = repository
        self.factory = EnvironmentFactory()
        self.actions = RuntimeActions()

    def initialize(self, mission_run_id: int, profile_alias: str, mission_id: str) -> RuntimeState:
        state = self.factory.build(mission_run_id, profile_alias, mission_id)
        self.repository.save(state)
        self.event_bus.publish(
            DomainEvent(
                event_type=EventTypes.RUNTIME_INITIALIZED,
                source="runtime.engine",
                profile_alias=profile_alias,
                mission_id=mission_id,
                payload={"run_id": mission_run_id},
            )
        )
        return state

    def current_state(self, mission_run_id: int) -> RuntimeState | None:
        return self.repository.load(mission_run_id)

    def inspect_nodes(self, mission_run_id: int) -> tuple[RuntimeState, str]:
        state = self.repository.load(mission_run_id)
        if state is None:
            raise RuntimeError(f"Runtime state not found for run_id={mission_run_id}")

        state, message = self.actions.inspect_nodes(state)
        self.repository.save(state)
        self._emit_runtime_action(state, "inspect_nodes", {"run_id": mission_run_id})
        return state, message

    def enumerate_services(self, mission_run_id: int, node_id: str) -> tuple[RuntimeState, str]:
        state = self.repository.load(mission_run_id)
        if state is None:
            raise RuntimeError(f"Runtime state not found for run_id={mission_run_id}")

        state, message = self.actions.enumerate_services(state, node_id)
        self.repository.save(state)
        self._emit_runtime_action(state, "enumerate_services", {"run_id": mission_run_id, "node_id": node_id})
        return state, message

    def establish_foothold(self, mission_run_id: int, node_id: str) -> tuple[RuntimeState, str]:
        state = self.repository.load(mission_run_id)
        if state is None:
            raise RuntimeError(f"Runtime state not found for run_id={mission_run_id}")

        state, message = self.actions.establish_foothold(state, node_id)
        self.repository.save(state)
        self._emit_runtime_action(state, "establish_foothold", {"run_id": mission_run_id, "node_id": node_id})
        return state, message

    def _emit_runtime_action(self, state: RuntimeState, action: str, payload: dict) -> None:
        self.event_bus.publish(
            DomainEvent(
                event_type=EventTypes.RUNTIME_ACTION,
                source="runtime.engine",
                profile_alias=state.profile_alias,
                mission_id=state.mission_id,
                payload={"action": action, **payload},
            )
        )
        self.event_bus.publish(
            DomainEvent(
                event_type=EventTypes.RUNTIME_STATE_CHANGED,
                source="runtime.engine",
                profile_alias=state.profile_alias,
                mission_id=state.mission_id,
                payload={
                    "run_id": state.mission_run_id,
                    "identified_entry_path": state.identified_entry_path,
                    "established_foothold": state.established_foothold,
                },
            )
        )
