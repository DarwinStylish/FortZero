"""Scan models for FortZero."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScanResult:
    action: str
    summary: str
