"""SQLite-backed profile repository."""

from __future__ import annotations

from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.profile.models import PlayerProfile, utc_now_iso


class ProfileRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def list_profiles(self) -> list[PlayerProfile]:
        query = """
        SELECT alias, preferred_mode, created_at, last_opened_at
        FROM profiles
        ORDER BY last_opened_at DESC
        """
        with get_connection(self.db_file) as connection:
            rows = connection.execute(query).fetchall()

        return [
            PlayerProfile(
                alias=row["alias"],
                preferred_mode=row["preferred_mode"],
                created_at=row["created_at"],
                last_opened_at=row["last_opened_at"],
            )
            for row in rows
        ]

    def exists(self, alias: str) -> bool:
        query = "SELECT 1 FROM profiles WHERE alias = ? LIMIT 1"
        with get_connection(self.db_file) as connection:
            row = connection.execute(query, (alias,)).fetchone()
        return row is not None

    def save(self, profile: PlayerProfile) -> None:
        query = """
        INSERT INTO profiles (alias, preferred_mode, created_at, last_opened_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(alias) DO UPDATE SET
            preferred_mode = excluded.preferred_mode,
            last_opened_at = excluded.last_opened_at
        """
        with get_connection(self.db_file) as connection:
            connection.execute(
                query,
                (
                    profile.alias,
                    profile.preferred_mode,
                    profile.created_at,
                    profile.last_opened_at,
                ),
            )
            connection.commit()

    def load(self, alias: str) -> PlayerProfile:
        query = """
        SELECT alias, preferred_mode, created_at, last_opened_at
        FROM profiles
        WHERE alias = ?
        """
        with get_connection(self.db_file) as connection:
            row = connection.execute(query, (alias,)).fetchone()

        if row is None:
            raise RuntimeError(f"Profile not found: {alias}")

        profile = PlayerProfile(
            alias=row["alias"],
            preferred_mode=row["preferred_mode"],
            created_at=row["created_at"],
            last_opened_at=utc_now_iso(),
        )
        self.save(profile)
        return profile
