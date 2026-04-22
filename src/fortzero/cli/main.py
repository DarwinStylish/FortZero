"""CLI entrypoint for FortZero."""

from __future__ import annotations

from fortzero.core.bootstrap import bootstrap_runtime, log_bootstrap
from fortzero.core.logging import configure_logging
from fortzero.shell.app import run_shell


def main() -> int:
    context = bootstrap_runtime()
    logger = configure_logging(
        level=context.config.logging.level,
        log_file=context.paths.log_file,
    )
    log_bootstrap(logger, context)
    return run_shell(context, logger)
