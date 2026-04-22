"""Discovery and scan engine for FortZero runtime."""

from __future__ import annotations

from fortzero.runtime.models import RuntimeState
from fortzero.runtime.scan_models import ScanResult


class ScanEngine:
    def surface_scan(self, state: RuntimeState) -> tuple[RuntimeState, ScanResult]:
        discovered_nodes = []

        for node in state.nodes:
            if not node.discovered:
                node.discovered = True
                discovered_nodes.append(node.hostname)

        if "Surface scan completed." not in state.notes:
            state.notes.append("Surface scan completed.")

        state.scan_history.append("surface_scan")

        if discovered_nodes:
            summary = f"Surface scan revealed nodes: {', '.join(discovered_nodes)}"
        else:
            summary = "Surface scan completed. No new nodes were revealed."

        return state, ScanResult(action="surface_scan", summary=summary)

    def service_scan(self, state: RuntimeState, node_id: str) -> tuple[RuntimeState, ScanResult]:
        node = next((n for n in state.nodes if n.id == node_id), None)
        if node is None:
            return state, ScanResult(action="service_scan", summary=f"Node not found: {node_id}")

        node.discovered = True
        visible_services = []

        for service in node.services:
            service.discovered = True
            visible_services.append(f"{service.name}/{service.port}")

        if node_id == "edge-gw":
            state.identified_entry_path = True
            if "Viable entry path identified through HTTPS login surface." not in state.notes:
                state.notes.append("Viable entry path identified through HTTPS login surface.")

        state.scan_history.append(f"service_scan:{node_id}")

        summary = (
            f"Service scan completed for {node.hostname}. "
            f"Visible services: {', '.join(visible_services)}"
        )
        return state, ScanResult(action="service_scan", summary=summary)

    def fingerprint_services(self, state: RuntimeState, node_id: str) -> tuple[RuntimeState, ScanResult]:
        node = next((n for n in state.nodes if n.id == node_id), None)
        if node is None:
            return state, ScanResult(action="fingerprint_services", summary=f"Node not found: {node_id}")

        node.discovered = True
        summaries = []

        for service in node.services:
            service.discovered = True
            summaries.append(f"{service.name}: {service.fingerprint}")

        state.scan_history.append(f"fingerprint_services:{node_id}")

        summary = (
            f"Fingerprinting completed for {node.hostname}. "
            + " | ".join(summaries)
        )
        return state, ScanResult(action="fingerprint_services", summary=summary)
