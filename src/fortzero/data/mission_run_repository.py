"""SQLite-backed mission run repository."""

from __future__ import annotations

import json
from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.mission.models import MissionRunState


class MissionRunRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def create_run(self, run_state: MissionRunState) -> int:
        query = """
        INSERT INTO mission_runs (
            profile_alias,
            campaign_id,
            mission_id,
            status,
            started_at,
            ended_at,
            objectives_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with get_connection(self.db_file) as connection:
            cursor = connection.execute(
                query,
                (
                    run_state.profile_alias,
                    run_state.campaign_id,
                    run_state.mission_id,
                    run_state.status,
                    run_state.started_at,
                    run_state.ended_at,
                    json.dumps([obj.__dict__ for obj in run_state.objectives], sort_keys=True),
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def update_run(self, run_id: int, run_state: MissionRunState) -> None:
        query = """
        UPDATE mission_runs
        SET status = ?, ended_at = ?, objectives_json = ?
        WHERE id = ?
        """
        with get_connection(self.db_file) as connection:
            connection.execute(
                query,
                (
                    run_state.status,
                    run_state.ended_at,
                    json.dumps([obj.__dict__ for obj in run_state.objectives], sort_keys=True),
                    run_id,
                ),
            )
            connection.commit()

    def completed_mission_ids(self, profile_alias: str, campaign_id: str) -> set[str]:
        query = """
        SELECT mission_id
        FROM mission_runs
        WHERE profile_alias = ?
          AND campaign_id = ?
          AND status = 'completed'
        """
        with get_connection(self.db_file) as connection:
            rows = connection.execute(query, (profile_alias, campaign_id)).fetchall()
        return {row["mission_id"] for row in rows}
