"""SQLite-backed event log repository."""

from __future__ import annotations

import json
from pathlib import Path

from fortzero.data.db import get_connection
from fortzero.events.models import DomainEvent


class EventRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file

    def record(self, event: DomainEvent) -> None:
        query = """
        INSERT INTO event_log (
            event_type,
            occurred_at,
            source,
            mission_id,
            profile_alias,
            session_id,
            payload_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with get_connection(self.db_file) as connection:
            connection.execute(
                query,
                (
                    event.event_type,
                    event.occurred_at,
                    event.source,
                    event.mission_id,
                    event.profile_alias,
                    event.session_id,
                    json.dumps(event.payload, sort_keys=True),
                ),
            )
            connection.commit()
