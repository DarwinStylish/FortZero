"""Runtime models for FortZero target environments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ServiceState:
    name: str
    port: int
    state: str
    note: str = ""


@dataclass
class NodeState:
    id: str
    hostname: str
    role: str
    discovered: bool = False
    foothold: bool = False
    services: list[ServiceState] = field(default_factory=list)


@dataclass
class RuntimeState:
    mission_run_id: int
    profile_alias: str
    mission_id: str
    nodes: list[NodeState] = field(default_factory=list)
    identified_entry_path: bool = False
    established_foothold: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RuntimeState":
        nodes = []
        for raw_node in payload.get("nodes", []):
            services = [
                ServiceState(
                    name=svc["name"],
                    port=svc["port"],
                    state=svc["state"],
                    note=svc.get("note", ""),
                )
                for svc in raw_node.get("services", [])
            ]
            nodes.append(
                NodeState(
                    id=raw_node["id"],
                    hostname=raw_node["hostname"],
                    role=raw_node["role"],
                    discovered=raw_node.get("discovered", False),
                    foothold=raw_node.get("foothold", False),
                    services=services,
                )
            )

        return cls(
            mission_run_id=payload["mission_run_id"],
            profile_alias=payload["profile_alias"],
            mission_id=payload["mission_id"],
            nodes=nodes,
            identified_entry_path=payload.get("identified_entry_path", False),
            established_foothold=payload.get("established_foothold", False),
            notes=list(payload.get("notes", [])),
        )
