"""Configuration loading for FortZero."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    name: str
    env: str
    offline_mode: bool


@dataclass(frozen=True)
class RuntimeConfig:
    create_missing_dirs: bool


@dataclass(frozen=True)
class LoggingConfig:
    level: str
    file: str


@dataclass(frozen=True)
class FortZeroConfig:
    app: AppConfig
    runtime: RuntimeConfig
    logging: LoggingConfig


class ConfigError(RuntimeError):
    """Raised when config is missing or invalid."""


def _require_section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Missing or invalid config section: '{key}'")
    return value


def load_config(config_path: Path) -> FortZeroConfig:
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        raise ConfigError("Config root must be a mapping")

    app = _require_section(raw, "app")
    runtime = _require_section(raw, "runtime")
    logging_cfg = _require_section(raw, "logging")

    try:
        return FortZeroConfig(
            app=AppConfig(
                name=str(app["name"]),
                env=str(app["env"]),
                offline_mode=bool(app["offline_mode"]),
            ),
            runtime=RuntimeConfig(
                create_missing_dirs=bool(runtime["create_missing_dirs"]),
            ),
            logging=LoggingConfig(
                level=str(logging_cfg["level"]).upper(),
                file=str(logging_cfg["file"]),
            ),
        )
    except KeyError as exc:
        raise ConfigError(f"Missing required config key: {exc}") from exc
