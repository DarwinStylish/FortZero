"""World-state mutation rules for FortZero."""

from __future__ import annotations

from fortzero.world.models import WorldState


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


class WorldMutations:
    def apply_mission_completion(
        self,
        world_state: WorldState,
        mission_id: str,
    ) -> WorldState:
        _append_unique(world_state.completed_missions, mission_id)

        if mission_id == "m01_silent_entry":
            _append_unique(world_state.unlocked_missions, "m02_deep_access")
            _append_unique(world_state.discovered_intel, "rootborne.internal_surface")
            _append_unique(world_state.acquired_access, "initial_foothold")

        if mission_id == "m02_deep_access":
            _append_unique(world_state.unlocked_missions, "m03_final_objective")
            _append_unique(world_state.discovered_intel, "rootborne.target_path")
            _append_unique(world_state.acquired_access, "elevated_control")

        if mission_id == "m03_final_objective":
            _append_unique(world_state.discovered_intel, "rootborne.final_artifact_secured")
            _append_unique(world_state.acquired_access, "operation_rootborne_complete")

        return world_state
