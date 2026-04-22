"""Narrative engine for FortZero terminal missions."""

from __future__ import annotations

from pathlib import Path

from fortzero.content.models import MissionDefinition
from fortzero.narrative.briefing_renderer import render_classified_header
from fortzero.narrative.text_fx import timed_print


class NarrativeEngine:
    def __init__(self, content_root: Path) -> None:
        self.content_root = content_root

    def _mission_dir(self, mission: MissionDefinition) -> Path:
        return self.content_root / "campaigns" / mission.campaign_id / "missions" / mission.id

    def _read_optional_text(self, path: Path) -> str | None:
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8").strip()
        return text if text else None

    def render_mission_intro(self, mission: MissionDefinition, preferred_mode: str) -> None:
        mission_dir = self._mission_dir(mission)

        briefing_text = self._read_optional_text(mission_dir / "briefing.txt")
        intel_text = self._read_optional_text(mission_dir / "intel.txt")
        hint_text = self._read_optional_text(mission_dir / "hint.txt")

        print("-" * 72)
        timed_print(render_classified_header(mission))
        print("-" * 72)

        if briefing_text:
            timed_print("MISSION BRIEFING")
            timed_print(briefing_text)
            print()

        if intel_text:
            timed_print("INTEL")
            timed_print(intel_text)
            print()

        if preferred_mode == "agent" and hint_text:
            timed_print("AGENT GUIDANCE")
            timed_print(hint_text)
            print()
