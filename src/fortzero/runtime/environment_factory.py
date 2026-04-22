"""Factory for deterministic FortZero mission environments."""

from __future__ import annotations

from fortzero.runtime.models import NodeState, RuntimeState, ServiceState


class EnvironmentFactory:
    def build(self, mission_run_id: int, profile_alias: str, mission_id: str) -> RuntimeState:
        if mission_id == "m01_silent_entry":
            return RuntimeState(
                mission_run_id=mission_run_id,
                profile_alias=profile_alias,
                mission_id=mission_id,
                nodes=[
                    NodeState(
                        id="edge-gw",
                        hostname="edge-gateway",
                        role="gateway",
                        discovered=True,
                        services=[
                            ServiceState(
                                name="ssh",
                                port=22,
                                state="filtered",
                                note="high friction",
                                fingerprint="OpenSSH-like edge daemon",
                                discovered=False,
                            ),
                            ServiceState(
                                name="https",
                                port=443,
                                state="open",
                                note="login surface",
                                fingerprint="Edge portal with operator login workflow",
                                discovered=False,
                            ),
                        ],
                    ),
                    NodeState(
                        id="wkst-01",
                        hostname="operator-workstation",
                        role="workstation",
                        discovered=False,
                        services=[
                            ServiceState(
                                name="rdp",
                                port=3389,
                                state="closed",
                                note="not externally reachable",
                                fingerprint="No exposed interactive desktop path",
                                discovered=False,
                            ),
                            ServiceState(
                                name="agent-beacon",
                                port=8443,
                                state="hidden",
                                note="not yet visible",
                                fingerprint="Dormant internal beacon channel",
                                discovered=False,
                            ),
                        ],
                    ),
                ],
                notes=["Environment seeded for Silent Entry."],
            )

        return RuntimeState(
            mission_run_id=mission_run_id,
            profile_alias=profile_alias,
            mission_id=mission_id,
            notes=["Generic environment initialized."],
        )
