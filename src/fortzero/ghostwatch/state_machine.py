"""GhostWatch posture state machine."""

from __future__ import annotations


class GhostWatchStateMachine:
    def posture_for_score(self, suspicion_score: int) -> str:
        if suspicion_score >= 6:
            return "hardened"
        if suspicion_score >= 4:
            return "alerted"
        if suspicion_score >= 2:
            return "watchful"
        return "calm"
