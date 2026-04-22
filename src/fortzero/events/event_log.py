"""Event log integration for FortZero."""

from __future__ import annotations

import logging

from fortzero.data.event_repository import EventRepository
from fortzero.events.models import DomainEvent


class EventLogger:
    def __init__(self, repository: EventRepository, logger: logging.Logger) -> None:
        self.repository = repository
        self.logger = logger

    def handle(self, event: DomainEvent) -> None:
        self.repository.record(event)
        self.logger.info(
            "Event recorded: type=%s source=%s profile=%s session=%s",
            event.event_type,
            event.source,
            event.profile_alias,
            event.session_id,
        )
