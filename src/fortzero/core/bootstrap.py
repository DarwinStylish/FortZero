"""Bootstrap runtime context for FortZero."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from fortzero.core.config import FortZeroConfig, load_config
from fortzero.core.paths import AppPaths, build_paths


@dataclass(frozen=True)
class BootstrapContext:
    paths: AppPaths
    config: FortZeroConfig


class BootstrapError(RuntimeError):
    """Raised when runtime bootstrap fails."""


def bootstrap_runtime() -> BootstrapContext:
    paths = build_paths()

    config = load_config(paths.config_file)

    required_dirs = [
        paths.data_dir,
        paths.logs_dir,
        paths.docs_dir,
        paths.content_dir,
        paths.labs_dir,
    ]

    if config.runtime.create_missing_dirs:
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)

    for directory in required_dirs:
        if not directory.exists():
            raise BootstrapError(f"Required directory missing: {directory}")

    return BootstrapContext(paths=paths, config=config)


def log_bootstrap(logger: logging.Logger, context: BootstrapContext) -> None:
    logger.info("Project root resolved: %s", context.paths.project_root)
    logger.info("Config loaded: %s", context.paths.config_file)
    logger.info("Offline mode: %s", context.config.app.offline_mode)
    logger.info("Runtime directories ready")
