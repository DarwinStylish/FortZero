"""GhostWatch response text for FortZero."""

from __future__ import annotations


class GhostWatchResponders:
    def message_for_posture(self, posture: str) -> str:
        if posture == "watchful":
            return "GhostWatch posture shifted to WATCHFUL. Defensive sensitivity is increasing."
        if posture == "alerted":
            return "GhostWatch posture shifted to ALERTED. Operator noise is now materially risky."
        if posture == "hardened":
            return "GhostWatch posture shifted to HARDENED. Future actions are under elevated scrutiny."
        return "GhostWatch remains CALM."
