"""SQLite-backed session repository."""

from __future__ import annotations

from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.profile.models import utc_now_iso


class SessionRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def start_session(self, profile_alias: str) -> int:
        query = """
        INSERT INTO sessions (profile_alias, started_at, active)
        VALUES (?, ?, 1)
        """
        with get_connection(self.db_file) as connection:
            cursor = connection.execute(query, (profile_alias, utc_now_iso()))
            connection.commit()
            return int(cursor.lastrowid)

    def end_session(self, session_id: int) -> None:
        query = """
        UPDATE sessions
        SET ended_at = ?, active = 0
        WHERE id = ?
        """
        with get_connection(self.db_file) as connection:
            connection.execute(query, (utc_now_iso(), session_id))
            connection.commit()
