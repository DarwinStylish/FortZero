"""Briefing renderer for FortZero mission startup."""

from __future__ import annotations

from fortzero.content.models import MissionDefinition


def render_classified_header(mission: MissionDefinition) -> str:
    return "\n".join(
        [
            "[CLASSIFIED]",
            f"Operation Mission: {mission.title}",
            f"Mission ID: {mission.id}",
            f"Campaign: {mission.campaign_id}",
            f"Risk Posture: ELEVATED",
        ]
    )
