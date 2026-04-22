"""SQLite-backed runtime-state repository."""

from __future__ import annotations

import json
from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.profile.models import utc_now_iso
from fortzero.runtime.models import RuntimeState


class RuntimeRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def load(self, mission_run_id: int) -> RuntimeState | None:
        query = """
        SELECT state_json
        FROM runtime_state
        WHERE mission_run_id = ?
        """
        with get_connection(self.db_file) as connection:
            row = connection.execute(query, (mission_run_id,)).fetchone()

        if row is None:
            return None

        payload = json.loads(row["state_json"])
        return RuntimeState.from_dict(payload)

    def save(self, state: RuntimeState) -> None:
        query = """
        INSERT INTO runtime_state (mission_run_id, profile_alias, mission_id, state_json, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(mission_run_id) DO UPDATE SET
            state_json = excluded.state_json,
            updated_at = excluded.updated_at
        """
        with get_connection(self.db_file) as connection:
            connection.execute(
                query,
                (
                    state.mission_run_id,
                    state.profile_alias,
                    state.mission_id,
                    json.dumps(state.to_dict(), sort_keys=True),
                    utc_now_iso(),
                ),
            )
            connection.commit()
