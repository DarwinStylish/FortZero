"""Terminal-safe text effects for FortZero."""

from __future__ import annotations

import sys
import time


def timed_print(text: str, delay: float = 0.0) -> None:
    """
    Print text line by line with an optional delay between lines.
    Keep delay at 0 by default so tests remain fast and non-fragile.
    """
    for line in text.splitlines():
        print(line)
        sys.stdout.flush()
        if delay > 0:
            time.sleep(delay)
