"""Minimal shell boot flow for PR1."""

from __future__ import annotations

import logging

from fortzero.core.bootstrap import BootstrapContext
from fortzero.shell.banner import render_banner


def run_shell(context: BootstrapContext, logger: logging.Logger) -> int:
    print(render_banner())
    print(f"App: {context.config.app.name}")
    print(f"Environment: {context.config.app.env}")
    print(f"Offline mode: {context.config.app.offline_mode}")
    print(f"Project root: {context.paths.project_root}")
    print(f"Log file: {context.paths.log_file}")
    print()
    print("FortZero runtime skeleton ready.")
    print("Shell initialized successfully.")
    logger.info("Shell initialized successfully")
    return 0
