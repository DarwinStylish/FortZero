"""SQLite-backed world-state repository."""

from __future__ import annotations

import json
from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.profile.models import utc_now_iso
from fortzero.world.models import WorldState


class WorldRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def load(self, profile_alias: str) -> WorldState:
        query = """
        SELECT state_json
        FROM world_state
        WHERE profile_alias = ?
        """
        with get_connection(self.db_file) as connection:
            row = connection.execute(query, (profile_alias,)).fetchone()

        if row is None:
            return WorldState(profile_alias=profile_alias)

        payload = json.loads(row["state_json"])
        return WorldState.from_dict(profile_alias, payload)

    def save(self, world_state: WorldState) -> None:
        query = """
        INSERT INTO world_state (profile_alias, state_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(profile_alias) DO UPDATE SET
            state_json = excluded.state_json,
            updated_at = excluded.updated_at
        """
        with get_connection(self.db_file) as connection:
            connection.execute(
                query,
                (
                    world_state.profile_alias,
                    json.dumps(world_state.to_dict(), sort_keys=True),
                    utc_now_iso(),
                ),
            )
            connection.commit()
