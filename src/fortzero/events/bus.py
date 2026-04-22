"""Synchronous in-process event bus for FortZero."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from fortzero.events.models import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._wildcard_subscribers: list[EventHandler] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._wildcard_subscribers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._wildcard_subscribers:
            handler(event)

        for handler in self._subscribers.get(event.event_type, []):
            handler(event)
