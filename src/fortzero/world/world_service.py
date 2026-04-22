"""World-state service for FortZero."""

from __future__ import annotations

from pathlib import Path

from fortzero.world.models import WorldState
from fortzero.world.world_mutations import WorldMutations
from fortzero.world.world_repository import WorldRepository


class WorldService:
    def __init__(self, db_file: Path) -> None:
        self.repository = WorldRepository(db_file)
        self.mutations = WorldMutations()

    def load(self, profile_alias: str) -> WorldState:
        return self.repository.load(profile_alias)

    def save(self, world_state: WorldState) -> None:
        self.repository.save(world_state)

    def apply_mission_completion(self, profile_alias: str, mission_id: str) -> WorldState:
        world_state = self.load(profile_alias)
        world_state = self.mutations.apply_mission_completion(world_state, mission_id)
        self.save(world_state)
        return world_state
