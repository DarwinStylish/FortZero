"""Validation helpers for FortZero content manifests."""

from __future__ import annotations

from typing import Any


class ContentValidationError(RuntimeError):
    """Raised when campaign or mission content is invalid."""


def require_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContentValidationError(f"{context} must be a mapping")
    return value


def require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContentValidationError(f"{context} must be a list")
    return value


def require_str(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContentValidationError(f"{context} must be a non-empty string")
    return value.strip()


def require_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise ContentValidationError(f"{context} must be a boolean")
    return value


def validate_required_keys(data: dict[str, Any], required: list[str], context: str) -> None:
    missing = [key for key in required if key not in data]
    if missing:
        raise ContentValidationError(
            f"{context} is missing required keys: {', '.join(missing)}"
        )
