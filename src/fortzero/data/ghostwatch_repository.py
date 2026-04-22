"""SQLite-backed GhostWatch repository."""

from __future__ import annotations

import json
from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.ghostwatch.models import GhostWatchState
from fortzero.profile.models import utc_now_iso


class GhostWatchRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def load(self, mission_run_id: int) -> GhostWatchState | None:
        query = """
        SELECT mission_run_id, profile_alias, mission_id, suspicion_score, posture, state_json
        FROM ghostwatch_state
        WHERE mission_run_id = ?
        """
        with get_connection(self.db_file) as connection:
            row = connection.execute(query, (mission_run_id,)).fetchone()

        if row is None:
            return None

        payload = json.loads(row["state_json"])
        state = GhostWatchState(
            mission_run_id=row["mission_run_id"],
            profile_alias=row["profile_alias"],
            mission_id=row["mission_id"],
            suspicion_score=row["suspicion_score"],
            posture=row["posture"],
            signals=list(payload.get("signals", [])),
        )
        return state

    def save(self, state: GhostWatchState) -> None:
        state.updated_at = utc_now_iso()
        query = """
        INSERT INTO ghostwatch_state (
            mission_run_id,
            profile_alias,
            mission_id,
            suspicion_score,
            posture,
            state_json,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(mission_run_id) DO UPDATE SET
            suspicion_score = excluded.suspicion_score,
            posture = excluded.posture,
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
                    state.suspicion_score,
                    state.posture,
                    json.dumps({"signals": state.signals}, sort_keys=True),
                    state.updated_at,
                ),
            )
            connection.commit()
