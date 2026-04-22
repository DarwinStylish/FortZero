"""Runtime action handlers for FortZero."""

from __future__ import annotations

from fortzero.runtime.models import RuntimeState


class RuntimeActions:
    def inspect_nodes(self, state: RuntimeState) -> tuple[RuntimeState, str]:
        for node in state.nodes:
            node.discovered = True
        if "Node inventory inspected." not in state.notes:
            state.notes.append("Node inventory inspected.")
        return state, "Node inventory inspected. Additional assets are now visible."

    def enumerate_services(self, state: RuntimeState, node_id: str) -> tuple[RuntimeState, str]:
        target = next((node for node in state.nodes if node.id == node_id), None)
        if target is None:
            return state, f"Node not found: {node_id}"

        target.discovered = True

        if node_id == "edge-gw":
            state.identified_entry_path = True
            for service in target.services:
                service.discovered = True
            if "Viable entry path identified through HTTPS login surface." not in state.notes:
                state.notes.append("Viable entry path identified through HTTPS login surface.")
            return state, "Service enumeration complete. A viable entry path has been identified."

        for service in target.services:
            service.discovered = True
        return state, f"Service enumeration complete for node: {node_id}"

    def establish_foothold(self, state: RuntimeState, node_id: str) -> tuple[RuntimeState, str]:
        target = next((node for node in state.nodes if node.id == node_id), None)
        if target is None:
            return state, f"Node not found: {node_id}"

        if not state.identified_entry_path:
            return state, "Cannot establish foothold before identifying a viable entry path."

        target.discovered = True
        target.foothold = True
        state.established_foothold = True

        if "Initial foothold established on target environment." not in state.notes:
            state.notes.append("Initial foothold established on target environment.")

        return state, f"Foothold established on node: {node_id}"
