"""Path helpers for FortZero."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    project_root: Path
    config_dir: Path
    data_dir: Path
    logs_dir: Path
    docs_dir: Path
    content_dir: Path
    labs_dir: Path
    profiles_dir: Path
    sessions_dir: Path
    config_file: Path
    log_file: Path
    db_file: Path


def resolve_project_root() -> Path:
    """
    Resolve the repository root from the installed src-layout package path.
    src/fortzero/core/paths.py -> parents[3] = repo root
    """
    return Path(__file__).resolve().parents[3]


def build_paths() -> AppPaths:
    root = resolve_project_root()
    config_dir = root / "config"
    data_dir = root / "data"
    logs_dir = root / "logs"

    return AppPaths(
        project_root=root,
        config_dir=config_dir,
        data_dir=data_dir,
        logs_dir=logs_dir,
        docs_dir=root / "docs",
        content_dir=root / "content",
        labs_dir=root / "labs",
        profiles_dir=data_dir / "profiles",
        sessions_dir=data_dir / "sessions",
        config_file=config_dir / "base.yaml",
        log_file=logs_dir / "fortzero.log",
        db_file=data_dir / "fortzero.db",
    )
