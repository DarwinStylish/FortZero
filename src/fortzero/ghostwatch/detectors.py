"""GhostWatch detectors for FortZero."""

from __future__ import annotations

from fortzero.events.models import DomainEvent, EventTypes


class GhostWatchDetectors:
    def signal_for_event(self, event: DomainEvent) -> tuple[str, int] | None:
        if event.event_type == EventTypes.OBJECTIVE_COMPLETED:
            if event.payload.get("duplicate", False):
                return ("duplicate_objective_completion", 2)
            return None

        if event.event_type == EventTypes.GHOSTWATCH_SIGNAL:
            reason = str(event.payload.get("reason", "generic_signal"))
            score = int(event.payload.get("score", 1))
            return (reason, score)

        return None
